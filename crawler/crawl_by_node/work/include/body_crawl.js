// html解析用
const HTMLParser = require('fast-html-parser');

exports.checkBodyAd = async (page, appLogger) => {
  //検索結果内AD 取得
  appLogger.info("===================");
  appLogger.info("AD list");
  appLogger.info("===================");

  let asinList = await page.$$eval(`div[data-asin] + div[class~='AdHolder']`, elementList => {
    var datas=[];

    for (let i = 0; i < elementList.length; i++) {
      var data = {
        asin: elementList[i].getAttribute('data-asin'),
        elementbody: elementList[i].innerHTML
      };
      datas.push(data);
    }
    return datas;
  });

  asinList.forEach(function( value ) {
    let doc = HTMLParser.parse(value.elementbody);
    let productNode = doc.querySelector('h2 a span')

    //ToDo:json形式に整形
    let addData = {asin : value.asin, name : productNode.lastChild.text}
    appLogger.info(addData);
  });
};
