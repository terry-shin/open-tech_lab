var log4js = require("log4js");
log4js.configure({
    appenders: {
        access: {type: 'file', filename: 'logs/access.log'},
        app: {type: 'file', filename: 'logs/app.log'},
        error: {type: 'file', filename: 'logs/err.log'}
    },
    categories: {
        default: {appenders:['app'], level: 'debug'},
        err: {appenders:['error'], level: 'warn'},
        web: {appenders:['access'], level: 'debug'}
    }
});

var appLogger = log4js.getLogger();
var errorLogger = log4js.getLogger('err');
var accessLogger = log4js.getLogger('web');


const express = require("express");
const app = express();
//bind access log
app.use(log4js.connectLogger(accessLogger));

// 環境変数にprotの指定がなければ8080使う
const PORT = process.env.PORT || 8080;
const HOST = '0.0.0.0';

app.listen(PORT, () => {
  console.log(`Server listening on port ${PORT}...`);
});


app.get("/", (req, res) => {
  appLogger.info("テスト index");
  res.send('Hello World');
});

//ここからcrawl検証

require('date-utils');

const dt = new Date();
var formatted = dt.toFormat('YYYYMMDDHH24MISS');

// puppeteer
const puppeteer = require('puppeteer');

// Cloudstrage
const {Storage} = require('@google-cloud/storage');
const storage = new Storage();
const myBucket = storage.bucket('test_bucket');

var msg;

const getTitle = page => {
  return page.title()
}

const getScreenShot = async page => {
  let buffer = await page.screenshot({fullPage: true});
  return buffer;
}

const getScreenShotLocal = async page => {
  console.log(`get img start`);
  await page.screenshot({
      path: `output/${formatted}_screenshot.png`,
      fullPage: true
  });
  console.log(`get img end`);
}


const saveStrage = buffer => {
  let file = myBucket.file(`${formatted}_screenshot.png`);
  file.save(buffer, { metadata: { contentType: 'image/png' } }).then(function() {});
}

const makeMsg = title => {
  console.log(`access:${title}`);
}

const sendError = err => {
  console.log(`error:${err}`);
}

app.get("/crawl", async (req, res) => {
  appLogger.info("テスト crawl");

  var keyword = req.query.k
  appLogger.info(`キーワード ${keyword}`);
  if (keyword == "" || keyword === undefined){
    res.status(200).send(`${formatted} no check END`);
  }

  //前準備
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
  await page.goto(encodeURI(`https://www.amazon.co.jp/s?k=${keyword}&__mk_ja_JP=%E3%82%AB%E3%82%BF%E3%82%AB%E3%83%8A&ref=nb_sb_noss`), {waitUntil: ["domcontentloaded", "networkidle0"]});

  //タイトル取得
  console.log(`get title`);
  getTitle(page).then(makeMsg).catch(sendError)

  //スクショ取得
  console.log(`get screenshot`);
  //await getScreenShot(page).then(saveStrage).catch(sendError)
  await getScreenShotLocal(page)

  await browser.close();

  res.status(200).send(`END:${formatted}`);
});
