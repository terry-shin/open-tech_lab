exports.checkBottomAd = async (adElem, appLogger) => {

  //BOTTOM 広告枠チェック
  bottomElems = await adElem.$$("div.threepsl-creative")
  if(bottomElems.length > 0){
    appLogger.info("===================");
    appLogger.info("BOTTOM AD list");
    appLogger.info("===================");
    for(let s=0; s < bottomElems.length; s++){
      let productItem = null;
      let productName = null;
      let linkItem = null;
      let productLink = null;

      //名前取得
      productItem = await bottomElems[s].$("div[data-headline] > span > span");
      if(productItem){
        productName = await (await productItem.getProperty('textContent')).jsonValue()
      }

      //リンク
      linkItem = await bottomElems[s].$("div > a");
      if(linkItem){
        productLink = await (await linkItem.getProperty('href')).jsonValue()
      }

      let addData = {name : productName, link : productLink}
      appLogger.info(addData);
    }
  }
};
