import requests


class APIRequestError(Exception):
    """Custom exception to handle API request failures."""
    pass


def fetch_order_filled_events(authorization_key, takerAssetId_list, n):
    """
    Fetch a specified number of orderFilledEvents using The Graph API, filtered by takerAssetId.

    Args:
        authorization_key (str): The Authorization Bearer token.
        takerAssetId_list (list): A list of takerAssetId values to filter by.
        n (int): The number of records to fetch.

    Returns:
        dict: The response from the API as a JSON object.

    Raises:
        APIRequestError: If the request fails or a non-200 status code is returned.
    """
    # Define the URL of the API endpoint
    url = "https://gateway.thegraph.com/api/subgraphs/id/81Dm16JjuFSrqz813HysXoUPvzTwE7fsfPk2RTf66nyC"

    # Define the headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {authorization_key}"
    }

    # Define the request payload
    payload = {
        "query": """
        query OrderFilledEvents($takerAssetIds: [String!], $first: Int!) {
          orderFilledEvents(
            first: $first,
            orderBy: timestamp,
            orderDirection: desc,
            where: { 
              takerAssetId_in: $takerAssetIds 
            }
          ) 
          {
            id
            timestamp
            orderHash
            takerAmountFilled
            maker {
              id
            }
            taker {
              id
            }
            takerAssetId
            makerAssetId
          }  
        }
        """,
        "operationName": "OrderFilledEvents",
        "variables": {
            "takerAssetIds": takerAssetId_list,
            "first": n
        }
    }

    try:
        # Make the POST request
        response = requests.post(url, headers=headers, json=payload)

        # Raise an exception for non-200 responses
        if response.status_code != 200:
            raise APIRequestError(f"Failed to fetch data. HTTP Status Code: {response.status_code}, Response: {response.text}")

        # Parse the response JSON
        data = response.json()

        # Check for errors in the GraphQL response
        if "errors" in data:
            raise APIRequestError(f"GraphQL API returned errors: {data['errors']}")

        # Return the retrieved data
        return data

    except requests.exceptions.RequestException as e:
        # Handle network-related issues
        raise APIRequestError(f"An error occurred while making the request: {e}") from e


def __dummy__():

    # Example usage:
    authorization_key = "abbdd04b6fc1b4d4a6b78be3d445ddda"
    takerAssetId_list = ["75808883562514695201169204487787555859570951708948163798444132865757266366758"]
    n = 5  # Number of records to fetch

    try:
        result = fetch_order_filled_events(authorization_key, takerAssetId_list, n)
        print(result)
    except APIRequestError as e:
        print(f"Error: {e}")


def __relete_ids_with_eventes():
    # https://thegraph.com/explorer/subgraphs/81Dm16JjuFSrqz813HysXoUPvzTwE7fsfPk2RTf66nyC?view=Query&chain=arbitrum-one

    self = ApiClient()

    slug = "russia-x-ukraine-ceasefire-before-october"
    markets = self.gamma.get_markets(slug=slug)
    markets[0]
    """
    {'id': '537194',
     'question': 'Russia x Ukraine ceasefire before October?',
     'conditionId': '0x41eda073eeca4071d3a643a527bf8549851ff16c7e4b924a007671cb11920f98',
     'slug': 'russia-x-ukraine-ceasefire-before-october',
     'resolutionSource': '',
     'endDate': '2025-09-30T12:00:00Z',
     'liquidity': '127995.0348',
     'startDate': '2025-04-14T19:43:35.184Z',
     'image': 'https://polymarket-upload.s3.us-east-2.amazonaws.com/russia-x-ukraine-ceasefire-before-july-GSNGh26whPic.jpg',
     'icon': 'https://polymarket-upload.s3.us-east-2.amazonaws.com/russia-x-ukraine-ceasefire-before-july-GSNGh26whPic.jpg',
     'description': 'This market will resolve to "Yes" if there is an official ceasefire agreement, defined as a publicly announced and mutually agreed halt in military engagement, between Russia and Ukraine by September 30, 2025, 11:59 PM ET.\n\nIf the agreement is officially reached before the resolution date, this market will resolve to "Yes," regardless of whether the ceasefire officially starts afterward.\n\nOnly ceasefires which constitute a general pause in the conflict will qualify. Ceasefires which only apply to energy infrastructure, the Black Sea, or other similar agreements will not qualify.\n\nAny form of informal agreement will not be considered an official ceasefire. Humanitarian pauses will not count toward the resolution of this market.\n\nThis market\'s resolution will be based on official announcements from both Russia and Ukraine; however, a wide consensus of credible media reporting stating an official ceasefire agreement between Russia and Ukraine has been reached will suffice.',
     'outcomes': '["Yes", "No"]',
     'outcomePrices': '["0.155", "0.845"]',
     'volume': '1455700.165243',
     'active': True,
     'closed': False,
     'marketMakerAddress': '',
     'createdAt': '2025-04-14T19:35:27.525312Z',
     'updatedAt': '2025-06-08T06:38:13.622206Z',
     'new': False,
     'featured': False,
     'submitted_by': '0x91430CaD2d3975766499717fA0D66A78D814E5c5',
     'archived': False,
     'resolvedBy': '0x6A9D222616C90FcA5754cd1333cFD9b7fb6a4F74',
     'restricted': True,
     'groupItemTitle': '',
     'groupItemThreshold': '0',
     'questionID': '0x13ef9a5be7e589e516317785a5b3be9ef44eda89d78debc30ad2450cf0af038b',
     'enableOrderBook': True,
     'orderPriceMinTickSize': 0.01,
     'orderMinSize': 5,
     'volumeNum': 1455700.165243,
     'liquidityNum': 127995.0348,
     'endDateIso': '2025-09-30',
     'startDateIso': '2025-04-14',
     'hasReviewedDates': True,
     'volume24hr': 20088.798792999998,
     'volume1wk': 368515.8268449999,
     'volume1mo': 915512.4083429999,
     'volume1yr': 1454605.4887740004,
     'gameStartTime': '2025-04-19 22:20:00+00',
     'clobTokenIds': '["75808883562514695201169204487787555859570951708948163798444132865757266366758", "79733714773966769289571596081594645290144843853077301462790845252981871229351"]',
     'umaBond': '500',
     'umaReward': '5',
     'volume24hrClob': 20088.798792999998,
     'volume1wkClob': 368515.8268449999,
     'volume1moClob': 915512.4083429999,
     'volume1yrClob': 1454605.4887740004,
     'volumeClob': 1455700.165243,
     'liquidityClob': 127995.0348,
     'acceptingOrders': True,
     'negRisk': False,
     'events': [{'id': '22805',
       'ticker': 'russia-x-ukraine-ceasefire-before-october',
       'slug': 'russia-x-ukraine-ceasefire-before-october',
       'title': 'Russia x Ukraine ceasefire before October?',
       'description': 'This market will resolve to "Yes" if there is an official ceasefire agreement, defined as a publicly announced and mutually agreed halt in military engagement, between Russia and Ukraine by September 30, 2025, 11:59 PM ET.\n\nIf the agreement is officially reached before the resolution date, this market will resolve to "Yes," regardless of whether the ceasefire officially starts afterward.\n\nOnly ceasefires which constitute a general pause in the conflict will qualify. Ceasefires which only apply to energy infrastructure, the Black Sea, or other similar agreements will not qualify.\n\nAny form of informal agreement will not be considered an official ceasefire. Humanitarian pauses will not count toward the resolution of this market.\n\nThis market\'s resolution will be based on official announcements from both Russia and Ukraine; however, a wide consensus of credible media reporting stating an official ceasefire agreement between Russia and Ukraine has been reached will suffice.',
       'resolutionSource': '',
       'startDate': '2025-04-14T19:44:37.379979Z',
       'creationDate': '2025-04-14T19:44:37.379976Z',
       'endDate': '2025-09-30T12:00:00Z',
       'image': 'https://polymarket-upload.s3.us-east-2.amazonaws.com/russia-x-ukraine-ceasefire-before-july-GSNGh26whPic.jpg',
       'icon': 'https://polymarket-upload.s3.us-east-2.amazonaws.com/russia-x-ukraine-ceasefire-before-july-GSNGh26whPic.jpg',
       'active': True,
       'closed': False,
       'archived': False,
       'new': False,
       'featured': True,
       'restricted': True,
       'liquidity': 127995.0348,
       'volume': 1455700.165243,
       'openInterest': 0,
       'createdAt': '2025-04-14T19:35:26.632563Z',
       'updatedAt': '2025-06-08T06:38:20.868348Z',
       'competitive': 0.8936350841134023,
       'volume24hr': 20088.798792999998,
       'volume1wk': 368515.8268449999,
       'volume1mo': 915512.4083429999,
       'volume1yr': 1454605.4887740004,
       'enableOrderBook': True,
       'liquidityClob': 127995.0348,
       'commentCount': -1,
       'series': [{'id': '10058',
         'ticker': 'russia-x-ukraine-ceasefire',
         'slug': 'russia-x-ukraine-ceasefire',
         'title': 'Russia x Ukraine Ceasefire',
         'seriesType': 'single',
         'recurrence': '',
         'image': 'https://polymarket-upload.s3.us-east-2.amazonaws.com/will-trump-issue-an-executive-order-on-february-14-IRIODX3MAqwP.jpg',
         'icon': 'https://polymarket-upload.s3.us-east-2.amazonaws.com/how-many-executive-orders-will-trump-sign-in-february-yNd2eOKrgBfO.jpg',
         'active': True,
         'closed': False,
         'archived': False,
         'featured': False,
         'restricted': True,
         'createdAt': '2025-03-13T05:04:52.248289Z',
         'updatedAt': '2025-06-08T06:38:22.253262Z',
         'volume': 27844447.741684,
         'liquidity': 822954.86179,
         'commentCount': 19027}],
       'cyom': False,
       'showAllOutcomes': True,
       'showMarketImages': True,
       'enableNegRisk': False,
       'automaticallyActive': True,
       'seriesSlug': 'russia-x-ukraine-ceasefire',
       'negRiskAugmented': False,
       'featuredOrder': 10,
       'pendingDeployment': False,
       'deploying': False}],
     'ready': False,
     'funded': False,
     'acceptingOrdersTimestamp': '2025-04-14T19:42:28Z',
     'cyom': False,
     'competitive': 0.8936350841134023,
     'pagerDutyNotificationEnabled': False,
     'approved': True,
     'clobRewards': [{'id': '21054',
       'conditionId': '0x41eda073eeca4071d3a643a527bf8549851ff16c7e4b924a007671cb11920f98',
       'assetAddress': '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174',
       'rewardsAmount': 0,
       'rewardsDailyRate': 200,
       'startDate': '2025-04-14',
       'endDate': '2500-12-31'}],
     'rewardsMinSize': 200,
     'rewardsMaxSpread': 3.5,
     'spread': 0.01,
     'oneDayPriceChange': -0.005,
     'oneWeekPriceChange': -0.13,
     'oneMonthPriceChange': -0.2,
     'lastTradePrice': 0.16,
     'bestBid': 0.15,
     'bestAsk': 0.16,
     'automaticallyActive': True,
     'clearBookOnStart': True,
     'manualActivation': False,
     'negRiskOther': False,
     'umaResolutionStatuses': '[]',
     'pendingDeployment': False,
     'deploying': False,
     'rfqEnabled': False}

    """

    # 'conditionId': '0x41eda073eeca4071d3a643a527bf8549851ff16c7e4b924a007671cb11920f98'
    # 'assetAddress': '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174'
    # 'clobTokenIds': '["75808883562514695201169204487787555859570951708948163798444132865757266366758", "79733714773966769289571596081594645290144843853077301462790845252981871229351"]',

    trades = self._clob_client.get_trades()
    trades[0]
    """
    {'id': '5e7793d0-5b85-48ac-8cb4-0d4f416b7f67',
     'taker_order_id': '0x73edadf4520010994e0020e286ece6d1e10376a198c9b0174f87285975808387',
     'market': '0x41eda073eeca4071d3a643a527bf8549851ff16c7e4b924a007671cb11920f98',
     'asset_id': '75808883562514695201169204487787555859570951708948163798444132865757266366758',
     'side': 'BUY',
     'size': '11',
     'fee_rate_bps': '0',
     'price': '0.16',
     'status': 'MINED',
     'match_time': '1749364472',
     'last_update': '1749364495',
     'outcome': 'Yes',
     'bucket_index': 0,
     'owner': '94a4a84a-379a-4c1a-743d-9eb348be557e',
     'maker_address': '0x94e44831dFc1F9F5C1c9216e7C4AF0aF43b43b11',
     'transaction_hash': '0x80b279fece57073ee6443a9a0111ecee507516fb4cc408931fc9117c11732096',
     'maker_orders': [{'order_id': '0x8bd6fda30abab42b46beaab3c57a2395b0440d7f0ed147df1c2b00d821719b05',
       'owner': '4e9eeb4b-e8df-0520-2be8-2bbd14c2b47d',
       'maker_address': '0x7C3Db723F1D4d8cB9C550095203b686cB11E5C6B',
       'matched_amount': '11',
       'price': '0.16',
       'fee_rate_bps': '0',
       'asset_id': '75808883562514695201169204487787555859570951708948163798444132865757266366758',
       'outcome': 'Yes',
       'side': 'SELL'}],
     'trader_side': 'TAKER'}
    """

    """
{
  orderFilledEvents(
    first: 1, 
    orderBy: timestamp, 
    orderDirection: desc,
    where: { 
      takerAssetId: "75808883562514695201169204487787555859570951708948163798444132865757266366758" 
    }
  ) 
  {
    id
    timestamp
    orderHash
    takerAmountFilled
  	maker{
      id
    }
  	taker{
      id
    }
		takerAssetId
  	makerAssetId
  	taker{
      id
  	}
  }  
}


    {
  "data": {
    "orderFilledEvents": [
      {
        "id": "0x80b279fece57073ee6443a9a0111ecee507516fb4cc408931fc9117c11732096_0x73edadf4520010994e0020e286ece6d1e10376a198c9b0174f87285975808387",
        "maker": {
          "id": "0x94e44831dfc1f9f5c1c9216e7c4af0af43b43b11"
        },
        "makerAssetId": "0",
        "orderHash": "0x73edadf4520010994e0020e286ece6d1e10376a198c9b0174f87285975808387",
        "taker": {
          "id": "0x4bfb41d5b3570defd03c39a9a4d8de6bd8b8982e"
        },
        "takerAmountFilled": "11000000",
        "takerAssetId": "75808883562514695201169204487787555859570951708948163798444132865757266366758",
        "timestamp": "1749364475"
      }
    ]
  }
}
    """


"""
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer abbdd04b6fc1b4d4a6b78be3d445ddda" \
  -d '{"query": "{ orderFilledEvents( first: 1, orderBy: timestamp, orderDirection: desc, where: { takerAssetId: "75808883562514695201169204487787555859570951708948163798444132865757266366758" } ) { id timestamp orderHash takerAmountFilled maker{ id } taker{ id } takerAssetId makerAssetId taker{ id } } }", "operationName": "Subgraphs", "variables": {}}' \
  https://gateway.thegraph.com/api/subgraphs/id/81Dm16JjuFSrqz813HysXoUPvzTwE7fsfPk2RTf66nyC
"""

