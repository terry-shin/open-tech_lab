exports.checkTopAd = async (adElem, appLogger) => {

  // TOP AD check
  headElems = await adElem.$$("div._multi-card-creative-desktop_DesktopContainer_content__EgtBX");
  if(headElems.length <= 0){
    headElems = await adElem.$$("div[data-cel-widget='MultiCardCreativeDesktop']");
  }

  if(headElems.length > 0){
    appLogger.info("===================");
    appLogger.info("TOP AD list");
    appLogger.info("===================");

    for(let s=0; s < headElems.length; s++){
      let asinList = await headElems[s].$$eval("div[data-asin]", elements => {
        return elements.map(data => data.getAttribute('data-asin'))
      });

      for(let x=0; x < asinList.length; x++){
        let asinItme = null;
        let productName = null;

        asinItem = await headElems[s].$(`div[data-asin='${asinList[x]}'] > div > a > span`);
        if(!asinItem){
          asinItem = await headElems[s].$("div[data-asin] span[data-click-el='title']");
        }
        if(asinItem){
          productName = await (await asinItem.getProperty('textContent')).jsonValue();
        }else{
          productName = "該当なし";
        }

        let addData = {asin : asinList[x], name : productName}
        appLogger.info(addData);
      }
    }
  }
};
