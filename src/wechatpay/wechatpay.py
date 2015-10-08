# -*- coding: utf-8 -*-

import hashlib
import requests
import xml.etree.ElementTree as ET

from utils import smart_str
from utils import get_noncestr


class WechatPay(object):
    """
    Wechat Pay
    ~~~~~~~~~~
    This class want to solve wechat payment problem.
    Before using this class, you need to set up the configuration of wechat
    payment.

    Usage::

        from wechatpay import WechatPay

        class Pay(WechatPay):

            appid = 'your_appid'
            appSecret = 'your_appSecret'
            mch_id = 'your_mch_id'
            partnerKey = 'your_partnerKey'
            notify_url = 'your_notify_url'

        ret = Pay().app_pay(params)
    """
    appid = ''
    appSecret = ''
    mch_id = ''
    partnerKey = ''
    notify_url = ''
    cert = ''

    PAY_URL = 'https://api.mch.weixin.qq.com/pay/unifiedorder'
    MICRO_PAY_URL = 'https://api.mch.weixin.qq.com/pay/micropay'
    BASE_PARAMS_KEYS = ['body', 'out_trade_no', 'total_fee', 'spbill_create_ip']
    PARAMS_DICT = {
        'NATIVE': ['product_id'],
        'JSAPI': ['openid'],
        'MICRO': ['auth_code'],
    }

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
        build wechat pay signature
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

    def _check_choose_params(self, transaction_id=None, out_trade_no=None):
        ret = {}
        if transaction_id:
            ret.update(transaction_id=transaction_id)
        elif not transaction_id and out_trade_no:
            ret.update(out_trade_no=out_trade_no)
        else:
            raise Exception('transaction_id or out_trade_no must have one')
        return ret

    def _check_params(self, keys, params):
        for key in keys:
            if not params.get(key):
                raise KeyError(key)

    def _request(self, url, params, retries=3, is_cert=False):
        if not isinstance(params, dict):
            raise Exception('params must be a dict')

        params['sign'] = self.build_sign(**params)

        xml_str = self.to_xml(**params)

        ret = {}
        error = None
        for i in xrange(retries):
            try:
                if is_cert:
                    r = requests.post(url, data=smart_str(xml_str),
                                      cert=self.cert)
                else:
                    r = requests.post(url, data=smart_str(xml_str))

                for child in ET.fromstring(smart_str(r.text)):
                    ret[child.tag] = child.text
                return ret
            except Exception as e:
                error = e
                continue
        raise 'Failed to request url, %s' % error

    def pay(self, params, trade_type='APP'):
        if not isinstance(params, dict):
            raise Exception('params must be a dict')

        # check params
        params_keys = self.BASE_PARAMS_KEYS[:]
        params_keys.extend(self.PARAMS_DICT.get(trade_type, []))
        self._check_params(params_keys, params)

        retries = params.pop('retries', 3)

        # params udpate config
        params.update({
            'appid': self.appid,
            'mch_id': self.mch_id,
            'nonce_str': get_noncestr(),
            'body': self.get_body(params.get('body')),
        })

        if trade_type != 'MICRO':
            params.update(notify_url=self.notify_url, trade_type=trade_type)

        url = self.MICRO_PAY_URL if trade_type == 'MICRO' else self.PAY_URL
        return self._request(url, params, retries=retries)

    def order_query(self, transaction_id=None, out_trade_no=None):
        # ducument: https://pay.weixin.qq.com/wiki/doc/api/micropay.php?chapter=9_2
        params = self._check_choose_params(transaction_id=transaction_id,
                                           out_trade_no=out_trade_no)
        url = 'https://api.mch.weixin.qq.com/pay/orderquery'
        params.update({
            'appid': self.appid,
            'mch_id': self.mch_id,
            'nonce_str': get_noncestr(),
        })
        return self._request(url, params)

    def order_reverse(self, out_trade_no, transaction_id=None):
        # document: https://pay.weixin.qq.com/wiki/doc/api/micropay.php?chapter=9_11&index=3
        params = {
            'appid': self.appid,
            'mch_id': self.mch_id,
            'nonce_str': get_noncestr(),
        }
        if transaction_id:
            params.update(transaction_id=transaction_id)
        else:
            params.update(out_trade_no=out_trade_no)

        url = 'https://api.mch.weixin.qq.com/secapi/pay/reverse'
        return self._request(url, params, is_cert=True)

    def order_refund(self, params):
        # document: https://pay.weixin.qq.com/wiki/doc/api/micropay.php?chapter=9_4
        transaction_id = params.pop('transaction_id', None)
        out_trade_no = params.pop('out_trade_no', None)
        params.update(self._check_choose_params(transaction_id=transaction_id,
                                                out_trade_no=out_trade_no))

        params_keys = ['out_refund_no', 'total_fee', 'refund_fee']
        self._check_params(params_keys, params)

        params['op_user_id'] = params.get('op_user_id', self.mch_id)

        url = 'https://api.mch.weixin.qq.com/secapi/pay/refund'
        params.update({
            'appid': self.appid,
            'mch_id': self.mch_id,
            'nonce_str': get_noncestr(),
        })
        return self._request(url, params, is_cert=True)

    def refund_order_query(self, params):
        # document: https://pay.weixin.qq.com/wiki/doc/api/micropay.php?chapter=9_5
        keys = ['transaction_id', 'out_trade_no', 'out_refund_no',
                'out_refund_no']
        is_True = False
        for key in keys:
            is_True = True if params.get(key) else is_True

        if not is_True:
            raise Exception('%s must have one' % ','.join(keys))

        params.update({
            'appid': self.appid,
            'mch_id': self.mch_id,
            'nonce_str': get_noncestr(),
        })
        url = 'https://api.mch.weixin.qq.com/pay/refundquery'
        return self._request(url, params)

    def short_url(self, long_url):
        # document: https://pay.weixin.qq.com/wiki/doc/api/micropay.php?chapter=9_9&index=8
        params = {
            'appid': self.appid,
            'mch_id': self.mch_id,
            'nonce_str': get_noncestr(),
            'long_url': long_url,
        }
        return self._request(url, params)

    def app_pay(self, params):
        """
        for app sdk pay
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
        for qr-code pay
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
        for JSAPI pay
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

    def micropay(self, params):
        """
        micro pay
        ~~~~~~~~~
        :param:
            body: your order title
            out_trade_no: your order id
            total_fee: your order price
            spbill_create_ip: ip address
            auth_code:
        :return:
            {
                'openid': '',
                'trade_type': 'MICROPAY',
                'cash_fee_type': None,
                'cash_fee': '1',
                'is_subscribe': 'N',
                'nonce_str': 'vswDZHsCkHUy50nA',
                'return_code': 'SUCCESS',
                'return_msg': 'OK',
                'sign': '02022866F63FAA5FEA4FEE2C7DF0C013',
                'bank_type': '',
                'attach': None,
                'mch_id': '',
                'out_trade_no': '',
                'transaction_id': '',
                'total_fee': '1',
                'appid': '',
                'fee_type': 'CNY',
                'time_end': '20151008160601',
                'result_code': 'SUCCESS'
            }
        """
        return self.pay(params, trade_type='MICRO')
