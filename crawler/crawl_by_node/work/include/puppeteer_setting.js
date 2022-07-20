// puppeteer
const puppeteer = require('puppeteer');

exports.getPage = async (keyword, appLogger) => {

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
  await page.goto(encodeURI(`https://www.amazon.co.jp/s?k=${keyword}`), {waitUntil: ["domcontentloaded", "networkidle0"]});

  return page;
};


exports.title = async page => {
  return await page.title();
};
