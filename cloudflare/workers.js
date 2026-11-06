// A modified worker to strip querystrings we don't need.

// These querystring keys are stripped from the request as they are generally not
// needed by the origin.
const STRIP_QUERYSTRING_KEYS = [
    'utm_source',
    'utm_campaign',
    'utm_medium',
    'utm_term',
    'utm_content',
    'gclid',
    'fbclid',
    'dm_i', // DotDigital
    'msclkid',
    'al_applink_data', // Meta outbound app links

    // https://docs.flying-press.com/cache/ignore-query-strings
    'age-verified',
    'ao_noptimize',
    'usqp',
    'cn-reloaded',
    'sscid',
    'ef_id',
    '_bta_tid',
    '_bta_c',
    'fb_action_ids',
    'fb_action_types',
    'fb_source',
    '_ga',
    'adid',
    '_gl',
    'gclsrc',
    'gdfms',
    'gdftrk',
    'gdffi',
    '_ke',
    'trk_contact',
    'trk_msg',
    'trk_module',
    'trk_sid',
    'mc_cid',
    'mc_eid',
    'mkwid',
    'pcrid',
    'mtm_source',
    'mtm_medium',
    'mtm_campaign',
    'mtm_keyword',
    'mtm_cid',
    'mtm_content',
    'epik',
    'pp',
    'pk_source',
    'pk_medium',
    'pk_campaign',
    'pk_keyword',
    'pk_cid',
    'pk_content',
    'redirect_log_mongo_id',
    'redirect_mongo_id',
    'sb_referer_host',
];

// If this is true, the querystring keys stripped from the request will be
// addeed to any Location header served by a redirect.
const REPLACE_STRIPPED_QUERYSTRING_ON_REDIRECT_LOCATION = false;

// If this is true, querystring key are stripped if they have no value eg. ?foo
// Disabled by default, but highly recommended
const STRIP_VALUELESS_QUERYSTRING_KEYS = false;

addEventListener('fetch', (event) => {
    event.respondWith(main(event));
});

async function main(event) {
    let { request } = event;
    let strippedParams;
    // eslint-disable-next-line prefer-const
    [request, strippedParams] = stripQuerystring(request);

    let response = await fetch(request);

    if (REPLACE_STRIPPED_QUERYSTRING_ON_REDIRECT_LOCATION) {
        response = replaceStrippedQsOnRedirectResponse(
            response,
            strippedParams,
        );
    }

    return response;
}

function stripQuerystring(request) {
    /**
     * Given a Request, return a new Request with the ignored or blank querystring keys stripped out,
     * along with an object representing the stripped values.
     */
    const url = new URL(request.url);

    const stripKeys = STRIP_QUERYSTRING_KEYS.filter((v) =>
        url.searchParams.has(v),
    );

    const strippedParams = {};

    if (stripKeys.length) {
        stripKeys.reduce((acc, key) => {
            acc[key] = url.searchParams.getAll(key);
            url.searchParams.delete(key);
            return acc;
        }, strippedParams);
    }

    if (STRIP_VALUELESS_QUERYSTRING_KEYS) {
        // Strip query params without values to avoid unnecessary cache misses
        url.searchParams.entries().forEach(([key, value]) => {
            if (!value) {
                url.searchParams.delete(key);
                strippedParams[key] = '';
            }
        });
    }

    return [new Request(url, request), strippedParams];
}

function replaceStrippedQsOnRedirectResponse(response, strippedParams) {
    /**
     * Given an existing Response, and an object of stripped querystring keys,
     * determine if the response is a redirect.
     * If it is, add the stripped querystrings to the location header.
     * This allows us to persist tracking querystrings (like UTM) over redirects.
     */

    if ([301, 302].includes(response.status)) {
        const redirectResponse = new Response(response.body, response);
        const locationHeaderValue = redirectResponse.headers.get('location');
        let locationUrl;

        if (!locationHeaderValue) {
            return redirectResponse;
        }

        const isAbsolute = isUrlAbsolute(locationHeaderValue);

        if (!isAbsolute) {
            // If the Location URL isn't absolute, we need to provide a Host so we can use
            // a URL object.
            locationUrl = new URL(
                locationHeaderValue,
                'http://www.example.com',
            );
        } else {
            locationUrl = new URL(locationHeaderValue);
        }

        Object.entries(strippedParams).forEach(([key, value]) =>
            locationUrl.searchParams.append(key, value),
        );

        let newLocation;

        if (isAbsolute) {
            newLocation = locationUrl.toString();
        } else {
            newLocation = `${locationUrl.pathname}${locationUrl.search}`;
        }

        redirectResponse.headers.set('location', newLocation);
        return redirectResponse;
    }

    return response;
}

function isUrlAbsolute(url) {
    return url.indexOf('://') > 0 || url.indexOf('//') === 0;
}
