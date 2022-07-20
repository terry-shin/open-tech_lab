const express = require("express");
const app = express();

app.get("/", (req, res) => {
res.send('Hello World');
});


// 環境変数にprotの指定がなければ8080使う
const PORT = process.env.PORT || 8080;
const HOST = '0.0.0.0';

app.listen(PORT, () => {
console.log(`Server listening on port ${PORT}...`);
});
