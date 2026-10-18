# Sungrow API

Small and compact Python library (`pysungrow`) plus a CLI tool (`sungrow`)
which implements a subset of the public Sungrow / iSolarCloud API.

## How to use

* Clone repo
* Check that things work:
    ```
    $ ./sungrow -h
    usage: sungrow [-h] ...
    ```
* Get an app key
    * Log in to the Sungrow developer portal. Either go from the iSolarCloud
      web site (there's a link in the top right), or go via
      https://developer-api.isolarcloud.com/
    * Make sure you choose correct server appropriate for your account. The
      server is shown when you log in, either in the app or on the web site.
      ("European server" or "international server" etc). If you choose the wrong
      server you won't be able to log in
    * Log-in credentials to the developer portal are the same as for the
      regular iSolarCloud web site and mobile app
    * Go to "applications" and "create application"
    * Choose a name, company name, description. Disable OAuth 2.0
      authentication
    * Submit, and your application should show up with "free plan"
    * View the application, note the "appkey" and the "secret key"
    * Browse the "documentation". The list of device types is relevant
      (appendix 1) as well as the lists of "measuring points"
    * Determine the API gateway URI for the appropriate server. This is listed
      in the developer portal documentation under "getting started" (e.g.
      `https://gateway.isolarcloud.eu/` for the "European server")

### CLI Usage

* Set log-in credentials:
    * `./sungrow set -k APPKEY -s SECRET_KEY -g GATEWAY_URI -u LOGIN_USER -p
      LOGIN_PASSWORD`
    * Example: `./sungrow set -k F62F692FBD3... -s kqtq8zh8... -g
      https://gateway.isolarcloud.eu -u dfx@dfx.at -p super-secret-password`
    * The `set` action simply stores these credentials in the state file
      (defaults to `.sungrow.yml` in your home directory). You can change these
      at any time later, and/or use multiple state files or put them in
      different locations (see `-f` option)
* Verify that the login actually works:
    * `./sungrow login`
    * No error printed means login was successful
    * It uses the credentials stored in the state file to actually log in to
      the iSolarCloud gateway, and obtain a login token (you can see it stored
      in the state file)
    * The login token is refreshed automatically as needed, so there is no need
      to manually perform the `login` action
* Pull the list of power plants associated with your account:
    * `./sungrow plant-list`
    * Prints one plant per line (it should print at least one)
    * The last item in the list is the numeric `ps-id` for the plant
* Pull the list of devices linked to a particular plant:
    * `./sungrow device-list --ps-id PSID`
    * Example: `./sungrow device-list --ps-id 9999999`
    * Prints one device per line
    * Note the serial, key (format `PSID_TYPE_X_X`), and type of each
      device
    * Does not print the device corresponding to the plant itself (type 11)
    * Check device type numbers against the list found in the developer portal
      documentation
* Print the details of the plant:
    * `./sungrow device-list --serial SERIAL`
    * Example: `./sungrow device-list --serial B99C99999`
    * Uses the serial number instead of the `ps-id` for some reason
    * Prints the key for device type 11 (the plant itself)
* Query metrics
    * `./sungrow metrics --device-type=TYPE --keys=KEY --keys=KEY ...
      --metrics=xxxxx --metrics=xxxxx ...`
    * Example: `./sungrow metrics --device-type=11 --keys=999999_11_0_0
      --metrics=83252 --metrics=83106 --metrics=83033`
    * Multiple devices (multiple keys) can be queried at the same time, but
      they must all be of the same type
    * Multiple metrics can be queried at the same time
    * Consult the documentation in the developer portal for possible metric IDs
      for each device type
    * Output is one line per device
    * The format of each line is: device key, space, followed by each metric
      separated by spaces. Metrics that didn't return a result are printed as a
      single dash `-`
    * Some useful metrics are obtainable from the "plant" device (type 11)
      while others are obtainable for individual other devices
* Historical metrics
    * `./sungrow historic [--interval=MINS] [--period=MINS --start=DATETIME
      --end=DATETIME] --keys=KEY --keys=KEY ...  --metrics=xxxxx
      --metrics=xxxxx ...`
    * Example: `./sungrow -v historic --period=120 --keys=999999_11_0_0
      --metrics=83252 --metrics=83106 --metrics=83033`
    * Similar to `metrics`, but returns a list of historic (stored) data points
      instead of the real-time values
    * Multiple metrics from multiple devices can be requested. All devices must
      be of the same time. Unlike with `metrics`, the device type is not
      required part of the request
    * The `interval` is the granularity of the returned time series, in
      minutes, defaulting to 15-minute steps
    * Start and end date/times must be given, in ISO 8601 format, without time
      zone information
        * Either start or end times may be omitted. The omitted time is then
          determined from the given `period` in minutes
        * If both start and end times have been omitted, then the end time is
          taken as the current time
        * Time zone is the plant's time zone
    * Output format is the same as `metrics` but includes the time stamp in ISO
      format as the second item in each line
