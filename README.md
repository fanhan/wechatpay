WechatPayment
=============

WechatPayment is a sdk for wechat payment, Before using this, you need to set up the configuration of wechat payment.


About payment, please read the [wechat payment document](https://pay.weixin.qq.com/wiki/doc/api/index.html)

#### how to install

```
git clone git@github.com:fanhan/wechatpay.git

cd wechatpay
python setup.py install
```



#### how to use?

```python
from wechatpay import WechatPayment

class Payment(WechatPayment):
	app_id = 'your_appid'
	mch_id = 'your_mch_id'
	appSecret = 'your_appSecret'
	partnerKey = 'your_partnerKey'
	notify_url = 'your_notify_url'

# for app sdk pay

params = {
	'body': '',
	'out_trade_no': '',
	'total_fee': 1,
	'fee_type': 'CNY',
	'spbill_create_ip': '127.0.0.1'
}

ret = Payment().app_pay(params)

# for qr code pay
params = {
	'body': '',
	'out_trade_no': '',
	'total_fee': 1,
	'fee_type': 'CNY',
	'spbill_create_ip': '127.0.0.1',
	'product_id': '1111'
}

ret = Payment().qrcode_pay(params)

# for jsapi pay

params = {
	'body': '',
	'out_trade_no': '',
	'total_fee': 1,
	'fee_type': 'CNY',
	'spbill_create_ip': '127.0.0.1',
	'openid': 'xxxxxx'   # from wechat service get openid
}

ret = Payment().jsapi_pay(params)
```

[how to get openid](https://pay.weixin.qq.com/wiki/doc/api/app.php?chapter=4_4)

#### TODO:

1. micro pay
