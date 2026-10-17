#!/usr/bin/env python3

import datetime
import pprint
import requests
import typing
import yaml


class Client:
    class _Config:
        app_key: str = None
        app_secret: str = None
        gateway: str = None
        username: str = None
        password: str = None
        token: str = None

    _c: _Config = _Config()
    _verbose: bool = False

    def __init__(self, verbose: bool = False):
        self._verbose = verbose

    def load_config(self, f: str) -> None:
        try:
            with open(f, "r") as fp:
                y = yaml.load(fp, yaml.SafeLoader)
                self.config(y)
        except Exception as e:
            pass

    def config(self, o: object | dict) -> None:
        for k in dir(self._c):
            if k[0] == "_":
                continue

            if isinstance(o, dict):
                if o.get(k):
                    self._c.__dict__[k] = o.get(k)
            elif isinstance(o, object):
                if o.__dict__.get(k):
                    self._c.__dict__[k] = o.__dict__.get(k)

    def write_config(self, f: str) -> None:
        try:
            with open(f, "w") as fp:
                yaml.dump(self._c.__dict__, fp)
        except Exception as e:
            print("failed to write config:" + e)

    def rreq(self, p: str, r: dict) -> dict:
        if not self._c.gateway:
            raise RuntimeError("missing gateway URL")
        if not self._c.app_key:
            raise RuntimeError("missing app key")
        if not self._c.app_secret:
            raise RuntimeError("missing app secret")

        r["appkey"] = self._c.app_key
        r["lang"] = "_en_US"

        hdrs = {
            "X-Access-Key": self._c.app_secret,
        }

        if self._verbose:
            print(f"sending request to {self._c.gateway}/openapi/{p}:")
            pprint.pp(r)

        rsp = requests.request(
            "POST", f"{self._c.gateway}/openapi/{p}", headers=hdrs, json=r
        )

        if self._verbose:
            print(f"response:")
            print(rsp)
            print(rsp.text)

        return rsp.json()

    def req(self, p: str, r: dict) -> dict:
        if not self._c.token:
            self.login()

        r["token"] = self._c.token
        rsp = self.rreq(p, r)

        if rsp["result_code"] == "E00003":  # token expired
            if self._verbose:
                print("login token expired, refreshing")
            self.login()
            r["token"] = self._c.token
            rsp = self.rreq(p, r)

        if rsp["result_code"] != "1":
            raise RuntimeError(f"API returned non-success\n{rsp}")

        return rsp

    def login(self) -> None:
        if not self._c.username:
            raise RuntimeError("missing username")
        if not self._c.password:
            raise RuntimeError("missing password")

        r = self.rreq(
            "login",
            {"user_account": self._c.username, "user_password": self._c.password},
        )

        self._c.token = r["result_data"]["token"]

    def plant_list(self) -> dict:
        r = self.req(
            "getPowerStationList",
            {"curPage": 1, "size": 10},
        )
        return r

    def device_list(self, ps_id: int) -> dict:
        r = self.req(
            "getDeviceList",
            {"curPage": 1, "size": 50, "ps_id": ps_id},
        )
        return r

    def plant_detail(self, serial: str) -> dict:
        r = self.req(
            "getPowerStationDetail",
            {"sn": serial},
        )
        return r

    def metrics(
        self, device_type: int, points: typing.List[str], key_list: typing.list[str]
    ) -> dict:
        r = self.req(
            "getDeviceRealTimeData",
            {
                "device_type": device_type,
                "point_id_list": points,
                "ps_key_list": key_list,
            },
        )
        return r

    def historic(
        self,
        points: typing.List[str],
        key_list: typing.list[str],
        interval: int | datetime.timedelta = 15,
        start: datetime.datetime | str | None = None,
        end: datetime.datetime | str | None = None,
        period: datetime.timedelta | int | float | None = None,
    ) -> dict:
        if isinstance(interval, datetime.timedelta):
            interval = int(interval.total_seconds() / 60)
        if start and isinstance(start, str):
            start = datetime.datetime.fromisoformat(start)
        if end and isinstance(end, str):
            end = datetime.datetime.fromisoformat(end)
        if period and (isinstance(period, int) or isinstance(period, float)):
            period = datetime.timedelta(minutes=period)

        if not start:
            if not period:
                raise RuntimeError("No time span has been given")
            if not end:
                end = datetime.datetime.now()
            start = end - period
        elif not end:
            if not period:
                raise RuntimeError("No time span has been given")
            end = start + period

        points = ",".join([f"p{p}" for p in points])

        r = self.req(
            "getDevicePointMinuteDataList",
            {
                "minute_interval": interval,
                "points": points,
                "ps_key_list": key_list,
                "start_time_stamp": start.strftime("%Y%m%d%H%M%S"),
                "end_time_stamp": end.strftime("%Y%m%d%H%M%S"),
            },
        )
        return r
