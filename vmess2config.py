import requests
import base64
from urllib.parse import urlparse
from urllib.parse import unquote
import json
import sys
import argparse


def download_and_decode(url, filename):
    response = requests.get(url)
    if not response.ok:
        sys.exit("download sunscribe link fail")
    with open(filename, "wb") as fd:
        for chunk in response.iter_content(chunk_size=128):
            fd.write(base64.b64decode(chunk, validate=True))


def parse_outbounds(filename):
    outbounds = []
    with open(filename, encoding="utf-8") as f:
        for line in f:
            parse_result = urlparse(unquote(line))
            if parse_result.scheme == "vmess":
                vmess = json.loads(base64.b64decode(parse_result.netloc, validate=True))
                if vmess.get("v") != "2":
                    sys.exit("not supportd vmess version")
                outbounds.append(parse_vmess_outbound(vmess))
    return outbounds


def parse_vmess_outbound(vmess):
    outbound_obj = {
        "protocol": "vmess",
        "settings": {
            "vnext": [],
        },
        "tag": "Proxy" + vmess["ps"],
        "streamSettings": {
            "network": vmess.get("net", "tcp"),
        },
    }
    outbound_obj["settings"]["vnext"].append(parse_server(vmess))
    if vmess.get("tls"):
        outbound_obj["streamSettings"]["security"] = vmess.get("tls")
    else:
        outbound_obj["streamSettings"]["security"] = "none"
    if outbound_obj["streamSettings"].get("security") == "tls":
        outbound_obj["tlsSettings"] = parse_tls(vmess)
    net = vmess.get("net")
    if net == "tcp":
        outbound_obj["streamSettings"]["tcpSettings"] = parse_tcp(vmess)
    if net == "kcp":
        outbound_obj["streamSettings"]["kcpSettings"] = parse_kcp(vmess)
    if net == "ws":
        outbound_obj["streamSettings"]["wsSettings"] = parse_ws(vmess)
    if net == "http" or net == "h2":
        outbound_obj["streamSettings"]["wsSettings"] = parse_http(vmess)
    if net == "quic":
        outbound_obj["streamSettings"]["quicSettings"] = parse_quic(vmess)
    if net == "grpc":
        outbound_obj["streamSettings"]["quicSettings"] = parse_grpc(vmess)
    return outbound_obj


def parse_server(vmess):
    server_obj = {}
    server_obj["address"] = vmess["add"]
    server_obj["port"] = int(vmess["port"])
    server_obj["users"] = [
        {
            "id": vmess["id"],
            "alterId": int(vmess["aid"]),
            "security": vmess.get("scy", "auto"),
        }
    ]
    return server_obj


def parse_tcp(vmess):
    tcp_obj = {
        "header": {
            "type": vmess.get("type", "none"),
        }
    }

    if vmess.get("host"):
        tcp_obj["header"]["request"] = {
            "version": "1.1",
            "method": "GET",
            "path": ["/"],
            "headers": {
                "Host": vmess.get("host", "").split(","),
                "User-Agent": [
                    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
                    "Mozilla/5.0 (iPhone; CPU iPhone OS 10_0_2 like Mac OS X) AppleWebKit/601.1 (KHTML, like Gecko) CriOS/53.0.2785.109 Mobile/14A456 Safari/601.1.46",
                ],
                "Accept-Encoding": ["gzip, deflate"],
                "Connection": ["keep-alive"],
                "Pragma": "no-cache",
            },
        }
    return tcp_obj


def parse_kcp(vmess):
    kcp_obj = {
        "header": {
            "type": vmess.get("type", "none"),
        },
        "seed": vmess.get("path", ""),
    }
    return kcp_obj


def parse_ws(vmess):
    ws_obj = {
        "path": vmess.get("path", "/"),
        "headers": {
            "Host": vmess.get("host", ""),
        },
    }
    return ws_obj


def parse_http(vmess):
    vmess["type"] = "http"
    http_obj = {
        "host": vmess.get("host", "").split(","),
        "path": vmess.get("path", "/"),
    }
    return http_obj


def parse_quic(vmess):
    quic_obj = {
        "security": vmess.get("host", "none"),
        "key": vmess.get("path", ""),
        "header": {
            "type": vmess.get("type", "none"),
        },
    }
    return quic_obj


def parse_grpc(vmess):
    grpc_obj = {
        "serviceName": vmess.get("path", ""),
    }
    return grpc_obj


def parse_tls(vmess):
    tls_obj = {
        "serverName": vmess.get("sni", ""),
        "alpn": vmess.get("alpn", "h2,http/1.1").split(","),
        "allowInsecure": True,
    }
    if vmess.get("fp"):
        tls_obj["pinnedPeerCertificateChainSha256"] = vmess.get("fp")
    return tls_obj


def gen_log():
    log_obj = {
        "loglevel": "warning",
    }
    return log_obj


def gen_dns():
    dns_obj = {
        "dns": {
            "hosts": {
                "dns.google": "8.8.8.8",
                "dns.pub": "119.29.29.29",
                "dns.alidns.com": "223.5.5.5",
                "geosite:category-ads-all": "127.0.0.1",
            },
            "servers": [
                {
                    "address": "https://1.1.1.1/dns-query",
                    "domains": ["geosite:geolocation-!cn"],
                    "expectIPs": ["geoip:!cn"],
                },
                "8.8.8.8",
                {
                    "address": "114.114.114.114",
                    "port": 53,
                    "domains": ["geosite:cn", "geosite:category-games@cn"],
                    "expectIPs": ["geoip:cn"],
                    "skipFallback": True,
                },
                {"address": "localhost", "skipFallback": True},
            ],
        }
    }
    return dns_obj


def gen_routing(balancers=[]):
    routing_obj = {
        "domainStrategy": "IPIfNonMatch",
        "domainMatcher": "mph",
        "rules": [
            {"type": "field", "outboundTag": "Direct", "protocol": ["bittorrent"]},
            {
                "type": "field",
                "outboundTag": "Dns-Out",
                "inboundTag": ["Socks-In", "Http-In"],
                "network": "udp",
                "port": 53,
            },
            {
                "type": "field",
                "outboundTag": "Reject",
                "domain": ["geosite:category-ads-all"],
            },
            {
                "type": "field",
                "balancerTag": "balancer",
                "domain": [
                    "full:www.icloud.com",
                    "domain:icloud-content.com",
                    "geosite:google",
                ],
            },
            {
                "type": "field",
                "outboundTag": "Direct",
                "domain": [
                    "geosite:tld-cn",
                    "geosite:icloud",
                    "geosite:category-games@cn",
                ],
            },
            {
                "type": "field",
                "balancerTag": "balancer",
                "domain": ["geosite:geolocation-!cn"],
            },
            {
                "type": "field",
                "outboundTag": "Direct",
                "domain": ["geosite:cn", "geosite:private"],
            },
            {
                "type": "field",
                "outboundTag": "Direct",
                "ip": ["geoip:cn", "geoip:private"],
            },
            {
                "type": "field",
                "balancerTag": "balancer",
                "network": "tcp,udp",
            },
        ],
        "balancers": balancers,
    }
    return routing_obj


def gen_extra_outbounds():
    extra_outbounds = [
        {
            "protocol": "dns",
            "tag": "Dns-Out",
        },
        {
            "protocol": "freedom",
            "tag": "Direct",
            "settings": {"domainStrategy": "UseIPv4"},
        },
        {
            "protocol": "blackhole",
            "tag": "Reject",
            # "settings": {"response": {"type": "http"}},
        },
    ]
    return extra_outbounds


def gen_inbounds(socks_port=1080, http_port=2080):
    inbounds = [
        {
            "protocol": "socks",
            "listen": "0.0.0.0",
            "port": socks_port,
            "tag": "Socks-In",
            "settings": {"ip": "127.0.0.1", "udp": True, "auth": "noauth"},
            "sniffing": {"enabled": True, "destOverride": ["http", "tls"]},
        },
        {
            "protocol": "http",
            "listen": "0.0.0.0",
            "port": http_port,
            "tag": "Http-In",
            "sniffing": {"enabled": True, "destOverride": ["http", "tls"]},
        },
    ]
    return inbounds


def gen_observatory():
    observatory_obj = {
        "subjectSelector": ["Proxy"],
    }
    return observatory_obj


def gen_balancers():
    balancers = [
        {
            "tag": "balancer",
            "selector": ["Proxy"],
            "strategy": {
                # v5 支持了 leastload
                "type": "leastPing",
            },
        },
    ]
    return balancers


def parse_vmesses(filename, socks_port, http_port, config_file):
    v2ray_obj = {
        "log": {},
        "dns": {},
        "inbounds": [],
        "outbounds": [],
        "routing": {},
        "observatory": {},
    }
    proxy_outbounds = parse_outbounds(filename)
    extra_outbounds = gen_extra_outbounds()
    v2ray_obj["outbounds"] = proxy_outbounds + extra_outbounds
    v2ray_obj["log"] = gen_log()
    v2ray_obj["dns"] = gen_dns()
    balancers = gen_balancers()
    v2ray_obj["routing"] = gen_routing(balancers=balancers)
    v2ray_obj["inbounds"] = gen_inbounds(socks_port=socks_port, http_port=http_port)
    v2ray_obj["observatory"] = gen_observatory()
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(v2ray_obj, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        "-u",
        "--url",
        help="generate v2ray config file from subscribe link",
    )
    arg_parser.add_argument(
        "-f",
        "--file",
        help="generate v2ray config file from filesystem",
    )
    arg_parser.add_argument(
        "-o",
        "--out",
        help="speifiy generate v2ray config filename",
    )
    arg_parser.add_argument(
        "--socks_port",
        help="socks inbound port",
        type=int,
    )
    arg_parser.add_argument(
        "--http_port",
        help="http inbound port",
        type=int,
    )

    args = arg_parser.parse_args()

    store_file = "vmesses.txt" if not args.file else args.file

    socks_port = 1080 if not args.socks_port else args.socks_port

    http_port = 2080 if not args.http_port else args.http_port

    config_file = "config.json"

    if args.url:
        download_and_decode(args.url, store_file)
        parse_vmesses(store_file, socks_port, http_port, config_file)

    if args.file:
        parse_vmesses(store_file, socks_port, http_port, config_file)
