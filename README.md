WechatPay
=============

WechatPay is a sdk for wechat pay, Before using this, you need to set up the configuration of wechat pay.


About pay, please read the [wechat pay document](https://pay.weixin.qq.com/wiki/doc/api/index.html)

#### how to install

```
git clone git@github.com:fanhan/wechatpay.git

cd wechatpay
python setup.py install
```

[how to get openid](https://pay.weixin.qq.com/wiki/doc/api/app.php?chapter=4_4)

#### how to use?

```python
from wechatpay import WechatPay

class Pay(WechatPay):
	appid = 'your_appid'
	mch_id = 'your_mch_id'
	appSecret = 'your_appSecret'
	partnerKey = 'your_partnerKey'
	notify_url = 'your_notify_url'
	# if need cert
	cert = '/path/your_cert.pem'

# for app sdk pay
params = {
	'body': '',
	'out_trade_no': '',
	'total_fee': 1,
	'fee_type': 'CNY',
	'spbill_create_ip': '127.0.0.1'
}

ret = Pay().app_pay(params)

# for qr code pay
params = {
	'body': '',
	'out_trade_no': '',
	'total_fee': 1,
	'fee_type': 'CNY',
	'spbill_create_ip': '127.0.0.1',
	'product_id': '1111'
}

ret = Pay().qrcode_pay(params)

# for jsapi pay
params = {
	'body': '',
	'out_trade_no': '',
	'total_fee': 1,
	'fee_type': 'CNY',
	'spbill_create_ip': '127.0.0.1',
	'openid': 'xxxxxx'   # from wechat service get openid
}

ret = Pay().jsapi_pay(params)

# for micropay
params = {
	'body': '',
	'out_trade_no': '',
	'total_fee': 1,
	'fee_type': 'CNY',
	'spbill_create_ip': '127.0.0.1',
	'auth_code': 'xxxxxx'
}

ret = Pay().micropay(params)

# order query
ret = Pay().order_query(transaction_id='xxxxx') or Pay().order_query(out_trade_no='xxxx')

# order reverse
# need cert
out_trade_no = 'xxxx'
ret = Pay().order_reverse(out_trade_no)

# order refund
# need cert
params = {
	'out_order_no': 'xxxx',
	'out_refund_no': 'xxxx',
	'total_fee': 1,
	'refund_fee': 1,
}
ret = Pay().order_refund(params)

# refund order query
params = {
	'out_order_no': 'xxxx',
}
ret = Pay().refund_order_query(params)
```
