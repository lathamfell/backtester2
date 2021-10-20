# will perform a Mongo query and then output the results to a csv. Compass is too slow now
import pymongo
import config_prod as c
import pandas as pd

#FILTER = {"valid": True, "_id.datafilename": "data/btcusd-5m_with_cols_2019_laguerre_1h_4h.csv"}

#FILTER = {"_id.winrate_floor": 0}
FILTER = {"_id.stop_loss": {"$gt": 0.5}}
FILTER = {"_id.take_profit": {"$gt": 0.5}}
FILTER = {"$expr": {"$eq": ["_id.stop_loss", "_id.take_profit"]}}


def main():
    mongo = pymongo.MongoClient(c.DB_CONNECTION)
    coll = mongo[c.DB][c.COLL]
    cur = coll.find(FILTER)
    print(f"{cur.count_documents({})} to output to csv")


if __name__ == "__main__":
    main()
