// html解析用
const HTMLParser = require('fast-html-parser');

exports.checkCartSeller = async (page, appLogger) => {
  //検索結果内AD 取得
  appLogger.info("===================");
  appLogger.info("Detail check");
  appLogger.info("===================");

  // メイン　部分取得
  let productMain = await page.$$("#dp-container");

  // 右部分 部分取得
  let cartDetail = await productMain[0].$$("#rightCol");
  // buyボックス 部分取得
  let buybox = await cartDetail[0].$$("#buybox");
  appLogger.info(buybox.length);

  // buyボックス 部分取得
  let sellerInfo = await buybox[0].$$("span.tabular-buybox-text > a");
  var test = await (await sellerInfo[0].getProperty('href')).jsonValue();
  var name = await (await sellerInfo[0].getProperty('textContent')).jsonValue();
  appLogger.info(name);
  appLogger.info(test);
};
