# -*- coding: utf-8 -*-

import json
import hashlib
import requests
import xml.etree.ElementTree as ET

from utils import smart_str, logger
from utils import get_noncestr


class WechatPayment(object):
    """
    Wechat Payment
    ~~~~~~~~~~
    This class want to solve wechat payment problem.
    Before using this class, you need to set up the configuration of wechat
    payment.

    Usage::

        from wechatpay import WechatPayment

        class Payment(WechatPayment):

            appid = 'your_appid'
            appSecret = 'your_appSecret'
            mch_id = 'your_mch_id'
            partnerKey = 'your_partnerKey'
            notify_url = 'your_notify_url'

        wechat_payment_sdk_params = Payment().app_pay(params)

    """
    appid = ''
    appSecret = ''
    mch_id = ''
    partnerKey = ''
    notify_url = ''

    PAYMENT_URL = 'https://api.mch.weixin.qq.com/pay/unifiedorder'
    BASE_PARAMS_KEYS = ['body', 'out_trade_no', 'total_fee', 'spbill_create_ip']
    PARAMS_DICT = {
        'NATIVE': ['product_id'],
        'JSAPI': ['openid'],
    }

    def _check_params(self, keys, params):
        for key in keys:
            if key not in params:
                raise KeyError(key)

    def create_sign_string(self, **kwargs):
        """
        get signature string
        """
        ret = []
        for k in sorted(kwargs.keys()):
            ret.append('%s=%s' % (k, kwargs[k]))

        sign_string = '&'.join(ret)
        return sign_string

    def build_sign(self, **kwargs):
        """
        build wechat payment signature
        """
        sign_temp = '%s&key=%s' % (self.create_sign_string(**kwargs),
                                   self.partnerKey)

        return hashlib.md5(smart_str(sign_temp)).hexdigest().upper()

    def to_xml(self, **kwargs):
        """
        dict to xml
        """
        xml_str = '<xml>'

        for k, v in kwargs.items():
            if isinstance(k, basestring):
                v = '<![CDATA[%s]]>' % v
            xml_str += '<%s>%s</%s>\n' % (k, v, k)

        xml_str += '</xml>'
        return xml_str

    def get_body(self, body):
        """
        body max length is 32
        """
        if len(body) >= 32:
            body = '%s...' % body[:28]
        return body

    def execute(self, params, retries=3):
        # params udpate config
        params.update({
            'appid': self.appid,
            'mch_id': self.mch_id,
            'notify_url': self.notify_url,
            'nonce_str': get_noncestr(),
            'body': self.get_body(params.get('body')),
        })

        # Get sign
        params['sign'] = self.build_sign(**params)

        # Set post xml str
        xml_str = self.to_xml(**params)

        ret = {}
        for i in xrange(retries):
            r = requests.post(self.PAYMENT_URL, data=smart_str(xml_str))

            for child in ET.fromstring(smart_str(r.text)):
                ret[child.tag] = child.text

            if ret.get('prepay_id'):
                logger.info('Successfully got prepay_id via UnifiedOrder, %s'
                            % json.dumps(ret))
                return ret

        logger.error('Failed to get prepay_id via UnifiedOrder, %s'
                     % json.dumps(ret))
        return {}

    def pay(self, params, trade_type='APP'):
        if not isinstance(params, dict):
            raise Exception('params is not a dict')

        # check params
        params_keys = self.BASE_PARAMS_KEYS[:]
        params_keys.extend(self.PARAMS_DICT.get(trade_type, []))
        self._check_params(params_keys, params)

        retries = params.pop('retries', 3)

        # set trade type
        params.update({
            'trade_type': trade_type,
        })

        return self.execute(params, retries=retries)

    def app_pay(self, params):
        """
        for app sdk payment
        ~~~~~~~~~~~~~~~~~~~
        :param
            body: your order title
            out_trade_no: your order id
            total_fee: your order price * 100
            spbill_create_ip: ip address

        :return
            {
                'trade_type': 'APP',
                'prepay_id': 'aaaaaa',
                'nonce_str': '1ylncjM8HwLDANi0',
                'return_code': 'SUCCESS',
                'return_msg': 'OK',
                'sign': '56C41ED1BB9823C7A5D8D04657CA5D22',
                'mch_id': 'your mch id',
                'appid': 'your appid'
            }
        """
        return self.pay(params, trade_type='APP')

    def qrcode_pay(self, params):
        """
        for qr-code payment
        ~~~~~~~~~~~~~~~~~~~
        :param:
            body: your order title
            out_trade_no: your order id
            total_fee: your order price * 100
            spbill_create_ip: ip address
            product_id: your product id
        :return
            {
                'trade_type': 'NATIVE',
                'prepay_id': 'xxxx',
                'nonce_str': '1jDVYGLDy1NzlPZ2',
                'return_code': 'SUCCESS',
                'return_msg': 'OK',
                'sign': '05E9FC6AB151F77817F193C636D50D84',
                'mch_id': 'your mch id',
                'appid': 'your app id',
                'code_url': 'weixin://wxpay/bizpayurl?pr=xxxxx',
            }
        """
        return self.pay(params, trade_type='NATIVE')

    def jsapi_pay(self, params):
        """
        for JSAPI payment
        ~~~~~~~~~~~~~~~~~~~
        :param:
            body: your order title
            out_trade_no: your order id
            total_fee: your order price
            spbill_create_ip: ip address
            openid:
        :return
            {
                'trade_type': 'JSSDK',
                'prepay_id': 'xxxx',
                'nonce_str': '1jDVYGLDy1NzlPZ2',
                'return_code': 'SUCCESS',
                'return_msg': 'OK',
                'sign': '05E9FC6AB151F77817F193C636D50D84',
                'mch_id': 'your mch id',
                'appid': 'your app id',
            }
        """
        return self.pay(params, trade_type='JSAPI')
