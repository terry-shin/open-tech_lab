//express
const express = require("express");
const app = express();
//キャッシュ
const cacheControl = require('express-cache-controller');
app.use(cacheControl({ maxAge: 0 }));

// output処理用
const fs = require("fs");

// log4js setting
const log4js = require("log4js");
log4js.configure('./work/config/log4js.config.json');

const appLogger = log4js.getLogger();
const errorLogger = log4js.getLogger('err');
const accessLogger = log4js.getLogger('web');

//bind access log
app.use(log4js.connectLogger(accessLogger));

// outputファイル用　現在日時設定する
require('date-utils');
const dt = new Date();
const formatted = dt.toFormat('YYYYMMDDHH24MISS');

// 環境変数にprotの指定がなければ8080使う
const PORT = process.env.PORT || 8080;
const HOST = '0.0.0.0';

app.listen(PORT, () => {
  console.log(`Server listening on port ${PORT}...`);
});

// index
app.get("/", (req, res) => {
  res.send('Hello World');
});


// ここからcrawl関連
// puppeteer
const puppeteer = require('puppeteer');

// Cloudstrage
const {Storage} = require('@google-cloud/storage');
const storage = new Storage();
const myBucket = storage.bucket('test_bucket');

// get page_title
const getTitle = async page => {
  return await page.title()
}

// get screenshot
const getScreenShot = async page => {
  let buffer = await page.screenshot({fullPage: true});
  return buffer;
}

//  screenshot save to LOCAL
const getScreenShotLocal = async page => {
  console.log(`save ScreenShot to LOCAL:START`);
  await page.screenshot({
      path: `./output/${formatted}_screenshot.png`,
      fullPage: true
  });
  console.log(`save ScreenShot to LOCAL:END`);
}

// save to CloudStrage
const saveStrage = buffer => {
  let file = myBucket.file(`${formatted}_screenshot.png`);
  file.save(buffer, { metadata: { contentType: 'image/png' } }).then(function() {});
}

// innerHTML save to LOCAL
const getHtmlLocal = async page => {
  console.log(`save innerHTML to LOCAL:START`);
  let html = await page.evaluate(() => { return document.getElementsByTagName('html')[0].innerHTML });

  await fs.writeFileSync(`./output/${formatted}_test.html`, html);
  console.log(`save innerHTML to LOCAL:END`);
}

const makeMsg = title => {
  console.log(`access:${title}`);
}

const sendError = err => {
  console.log(`error:${err}`);
}

// 取得
var top = require('./include/top_crawl');
var bottom = require('./include/bottom_crawl');
var body = require('./include/body_crawl');

var detail = require('./include/detail_crawl');

//キーワードクロール
const wrap = fn => (...args) => fn(...args).catch(args[2]);

app.get("/crawl", wrap(async (req, res, next) => {
  appLogger.info("crawl START");

  var outputJson;

  //get input_parameter
  var keyword = req.query.k;
  appLogger.info(`input keyword:${keyword}`);
  if (keyword == "" || keyword === undefined){
    res.status(200).send(`${formatted}：no check END`);
  }

  //puppeteer 前準備
  const browser = await puppeteer.launch({
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-gpu',
      '--disable-infobars',
      '--disable-application-cache',
      '--ignore-certificate-errors',
      ''
    ],
    defaultViewport: {
      width: 1280,
      height: 1696
    }
  });
  let page = (await browser.pages())[0];
  const userAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36';
  page.setUserAgent(userAgent);

  //ページ取得
  //url = `https://www.amazon.co.jp/s?k=${keyword}`
  url = 'https://www.amazon.co.jp/dp/B08SW2LN6Q/'
  await page.goto(encodeURI(url), {waitUntil: ["domcontentloaded", "networkidle0"]});

  //タイトル取得
  getTitle(page).then(makeMsg).catch(sendError)

  //スクショ & html取得
  appLogger.info(`get screenshot & html`);
  //google strageへ 環境によって分ける
  //await getScreenShot(page).then(saveStrage).catch(sendError)
  await getScreenShotLocal(page)
  await getHtmlLocal(page)

  // TOP&BOTTOM 広告枠取得
  let adElems = await page.$$("span[data-component-type='s-ads-metrics'");
  for(let i=0; i < adElems.length; i++){

    //TOP 広告枠チェック
    await top.checkTopAd(adElems[i], appLogger);

    //BOTTOM 広告枠チェック
    await bottom.checkBottomAd(adElems[i], appLogger);
  }

  //検索結果内AD 取得
  await body.checkBodyAd(page, appLogger);

  browser.close();
  res.status(200).send(`END:${formatted}`);
}));


app.get("/detail_crawl", wrap(async (req, res, next) => {
  appLogger.info("crawl START");

  var outputJson;

  //get input_parameter
  var asin = req.query.asin;
  appLogger.info(`input ASIN:${asin}`);
  if (asin == "" || asin === undefined){
    res.status(200).send(`${formatted}：no check END`);
  }

  //puppeteer 前準備
  const browser = await puppeteer.launch({
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-gpu',
      '--disable-infobars',
      '--disable-application-cache',
      '--ignore-certificate-errors',
      ''
    ],
    defaultViewport: {
      width: 1280,
      height: 1696
    }
  });
  let page = (await browser.pages())[0];
  const userAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.193 Safari/537.36';
  page.setUserAgent(userAgent);

  //ページ取得
  await page.goto(encodeURI(`https://www.amazon.co.jp/dp/${asin}/`), {waitUntil: ["domcontentloaded", "networkidle0"]});

  //タイトル取得
  getTitle(page).then(makeMsg).catch(sendError)

  //スクショ & html取得
  appLogger.info(`get screenshot & html`);
  //google strageへ 環境によって分ける
  //await getScreenShot(page).then(saveStrage).catch(sendError)
  await getScreenShotLocal(page)
  await getHtmlLocal(page)

  //検索結果内AD 取得
  await detail.checkCartSeller(page, appLogger);

  browser.close();
  res.status(200).send(`crawl END:${formatted}`);
}));
