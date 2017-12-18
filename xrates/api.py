import json, urllib2


def get_rate( code1, code2 ):
    cache_key = ( 'xrates-py:get_rate:%s-to-%s' % ( code1, code2 ) ).lower()
    rjson = cache.get( cache_key, None )

    if not rjson:
        headers = {
            'User-Agent': 'xrates-py',
        }
        url = ( 'https://www.xrates.net/api/rate/%s-to-%s.json' % ( code1, code2, ) ).lower()
        request = urllib2.Request( url, None, headers )

        try:
            response = urllib2.urlopen( request )
            rjson = response.read()
        except urllib2.HTTPError, e:
            if e.code == 404:
                rjson = '{}' # Not found, so empty array
            else:
                raise

        cache.add( cache_key, rjson )

    return json.loads( rjson )


def get_country_rate( countrycode, code2 ):
    cache_key = ( 'xrates-py:get_country_rate:%s-to-%s' % ( countrycode, code2 ) ).lower()
    rjson = cache.get( cache_key, None )

    if not rjson:
        headers = {
            'User-Agent': 'xrates-py',
        }
        url = ( 'https://www.xrates.net/api/country-rate/%s-to-%s.json' % ( countrycode, code2, ) ).lower()
        request = urllib2.Request( url, None, headers )

        try:
            response = urllib2.urlopen( request )
            rjson = response.read()
        except urllib2.HTTPError, e:
            if e.code == 404:
                rjson = '{}' # Not found, so empty array
            else:
                raise

        cache.add( cache_key, rjson )

    return json.loads( rjson )


def get_local_value( localcountry, usd_amount ):
    rjson = get_country_rate( localcountry, 'USD' )

    if rjson:
        value = usd_amount * float( rjson['rate'] )

        if json['to_symbol_is_prefixed']:
            return '%s%s' % ( rjson['to_symbol'], value )
        return '%s%s' % ( value, rjson['to_symbol'] )

    return 0
