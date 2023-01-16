# Copyright © 2020 Interplanetary Database Association e.V.,
# Planetmint and IPDB software contributors.
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

import pytest

from transactions.types.assets.create import Create
from ipld import marshal, multihash

METADATA_ENDPOINT = "/api/v1/metadata/"


@pytest.mark.bdb
def test_get_metadata_tendermint(client, b, alice):
    assets = [{"data": multihash(marshal({"msg": "abc"}))}]
    # test returns empty list when no assets are found
    res = client.get(METADATA_ENDPOINT + assets[0]["data"])
    assert res.json == []
    assert res.status_code == 200

    # create asset
    # asset #= {"msg": "abc"}
    metadata = multihash(marshal({"key": "my_meta"}))
    tx = Create.generate([alice.public_key], [([alice.public_key], 1)], metadata=metadata, assets=assets).sign(
        [alice.private_key]
    )

    b.store_bulk_transactions([tx])

    # test that metadata is returned
    res = client.get(METADATA_ENDPOINT + metadata)
    assert res.status_code == 200
    assert len(res.json) == 1
    assert res.json[0] == metadata


@pytest.mark.bdb
def test_get_metadata_limit_tendermint(client, b, alice):

    # create two assets
    assets1 = [{"data": multihash(marshal({"msg": "abc 1"}))}]
    meta = multihash(marshal({"key": "meta 1"}))
    tx1 = Create.generate([alice.public_key], [([alice.public_key], 1)], metadata=meta, assets=assets1).sign(
        [alice.private_key]
    )
    b.store_bulk_transactions([tx1])

    assets2 = [{"data": multihash(marshal({"msg": "abc 2"}))}]
    tx2 = Create.generate([alice.public_key], [([alice.public_key], 1)], metadata=meta, assets=assets2).sign(
        [alice.private_key]
    )
    b.store_bulk_transactions([tx2])

    # test that both assets are returned without limit
    res = client.get(METADATA_ENDPOINT + meta)
    assert res.status_code == 200
    assert len(res.json) == 2

    # test that only one asset is returned when using limit=1
    res = client.get(METADATA_ENDPOINT + meta + "?limit=1")
    assert res.status_code == 200
    assert len(res.json) == 1
