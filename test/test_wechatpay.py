# -*- coding:utf-8 -*-

import sys
sys.path.append('../src/')

from wechatpay import WechatPayment


class Payment(WechatPayment):
    appid = ''
    appSecret = ''
    partnerKey = ''
    notify_url = ''


def main():
    params = {
        'body': '',
        'out_trade_no': '',
        'total_fee': 1,
        'fee_type': '',
        'spbill_create_ip': ''
    }
    print Payment().app_pay(params)
    return

if __name__ == "__main__":
    main()
