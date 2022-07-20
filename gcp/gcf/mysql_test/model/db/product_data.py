from config.setting import Base, session
from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func


class ProductData(Base):
    """
    product_data Model
    """
    __tablename__ = 'product_data'
    asin = Column(String(50), primary_key=True)
    name = Column(String(255))
    brand = Column(String(50))
    manufacturer = Column(String(50))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def check_asin_exist(asin: str):
        """
        ASIN存在チェック

        Parameters
        ----------
        asin : str
            ASIN

        Returns
        -------
        corp_list : object
            法人情報オブジェクトリスト　取れない場合はFalse
        """
        result_list = session.query(ProductData).filter(ProductData.asin == asin)
        if result_list.count() > 0:
            return True
        return False
