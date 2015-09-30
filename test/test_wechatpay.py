# -*- coding:utf-8 -*-

from wechatpay import WechatPay


class Pay(WechatPay):
    appid = ''
    appSecret = ''
    partnerKey = ''
    notify_url = ''
    mch_id = ''


def main():
    params = {
        'body': '测试订单',
        'out_trade_no': 'local1231231241232',
        'total_fee': 1,
        'fee_type': 'CNY',
        'spbill_create_ip': '127.0.0.1',
        'product_id': 1231231,
    }
    print Pay().qrcode_pay(params)
    return

if __name__ == "__main__":
    main()
