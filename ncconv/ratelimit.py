from datetime import datetime, timedelta, timezone
import math
from typing import Callable

from fastapi import HTTPException, Request, Response


def ratelimit(key: str, limit: int, unit_time: timedelta) -> Callable:
    '''
    Returns a callable that can be used with depends() for rate limiting.

    While not strictly required, ideally limit and unit_time remain the same per key

    :param key: The rate limit group as a string
    :param limit: Limit per unit time as an int
    :param unit_time: Timedelta to apply this rate limit over
    '''
    async def do_limit(request: Request, response: Response):
        ratedata = await request.app.state.db.ratelimits.find_one({'ip': request.client.host, 'key': key})

        now = datetime.now(timezone.utc)

        if ratedata is None:
            ratedata = {
                'ip': request.client.host,
                'key': key,
                'accesses': [
                    now
                ],
                'bucket_expires': now + unit_time
            }

            await request.app.state.db.ratelimits.insert_one(ratedata)
            return
        
        new_accesses = []
        for access in ratedata['accesses']:
            # Motor does not seem to restore the timezone attributes for datetime objects, so we have to do this manually
            access = access.replace(tzinfo=timezone.utc)

            # append any accesses which still count against the rate limit
            if now - access < unit_time:
                new_accesses.append(access)
        
        if limit <= len(new_accesses):
            # ditto
            exp = ratedata['bucket_expires'].replace(tzinfo=timezone.utc)

            raise HTTPException(status_code=429, detail=f'You are being ratelimited. Check the Retry-After header.', headers={'Retry-After': f'{int(math.ceil((exp - now).total_seconds()))}'})

        new_accesses.append(now)

        await request.app.state.db.ratelimits.update_one({'ip': request.client.host, 'key': key}, {'$set': {'accesses': new_accesses, 'bucket_expires': now + unit_time}})

    return do_limit