import os
import requests
import logging
import json
import redis
import socket

from requests import Request, Session

from django.conf import settings
from django.contrib.sites.models import Site
from django.urls import reverse

logger = logging.getLogger(__name__)
REDIS_URL = os.environ.get('REDIS_URL', "redis://localhost:6379/0")
cache = redis.StrictRedis.from_url(url=REDIS_URL)
CURRENCY_CODE = "PLN"


def request_payu_token(
    url='https://secure.snd.payu.com/pl/standard/user/oauth/authorize',
    client_id=settings.PAYU_CLIENT_ID,
    client_secret=settings.PAYU_CLIENT_SECRET
):
    """
    Returns PayU Token needed to start the transaction
    :param url: URl to payU API
    :param client_id: taken from settings
    :param client_secret: taken from settings
    :return: Token or None if not possible
    """
    logger.info('Requesting PayU TOKEN!')
    payload = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    }

    response = requests.post(url, payload)
    logger.info(f'The response is: {response} {response.status_code} {response.content}')

    if response.status_code == 200:
        logger.info(f'replied with {response.status_code}')
        try:
            data = json.loads(response.text)
        except ValueError:
            return None
        return data.get('access_token')
    else:
        logger.debug(f'Response status_code == {response.status_code}')
        return None


def send_payu_order(
    order,
    request,
    url='https://secure.snd.payu.com/api/v2_1/orders',
):
    logger.debug('creating new order')
    notify_url = Site.objects.get_current().domain + reverse('notify-payments')
    continue_url = ''
    if request.is_secure():
        continue_url += 'https://'
    else:
        continue_url += 'http://'
    continue_url += Site.objects.get_current().domain + reverse('purchases')+"?payUResponse=1"
    print(f'notfiy_url: {notify_url}')
    payload = json.dumps({
        "notifyUrl": notify_url,
        "continueUrl": continue_url,
        "customerIp": order.customer_ip,
        "merchantPosId": str(settings.PAYU_POS_ID),
        "description": order.product.desc,
        "currencyCode": CURRENCY_CODE,
        "totalAmount": order.product.price,
        "extOrderId": str(order.order_id),
        "buyer": {
            "email": request.user.email,
            "firstName": request.user.first_name,
            "lastName": request.user.last_name
        },
        "products": [
            {
                "name": order.product.name,
                "unitPrice": order.product.price,
                "quantity": "1"
            }

        ],

    })

    if type(get_payu_token()) == 'string':
        authorization_bearer = f'Bearer {get_payu_token()}'
    else:
        authorization_bearer = f'Bearer {get_payu_token().decode("utf-8")}'

    headers = {
        "content-type": "application/json",
        "Authorization": authorization_bearer,
    }

    response = requests.post(
        url=url,
        data=payload,
        headers=headers,
        allow_redirects=False
    )

    if response.status_code == 302:

        try:
            data = json.loads(response.text)
            url = data.get('redirectUri')
            logger.debug(f"redirectUr == {url} and it's status {data.get('status')}")

            if url:
                return url
            else:
                logger.error(
                    u"Invalid PayU response, no redirectUri found."
                )
        except ValueError:
            logger.error(
                u"Invalid PayU response."
            )
    if response.status_code == 403:
        logger.error('Not allowed on PayU server - error 403! Check your configuration!')

    if response.status_code == 401:
        logger.error('Error 401, Check your token, authorization seems to be the problem.')
    else:
        logger.error(
            f"Invalid PayU order status code {response.status_code}, check your code."
        )

    return None


def get_payu_token():
    """
    Return token from cache if exists.

    If token does not exists request a new one, update cache and return it.
    Return None if failed
    :return:
    """
    logger.debug('Getting PayU Token')

    access_token = cache.get('payu_access_token')

    logger.debug(f'access token == {access_token}')

    if not access_token:
        logging.debug(f'No access token')
        access_token = request_payu_token()
        logging.debug(f'Requested access_token == {access_token}')
        if access_token:
            cache.setex('payu_access_token', 43199, access_token)
        else:
            return None
    return access_token
