# 這是測試檔案

git 指令

- git init .
- git clone 網址
  - 範例: git clone https://github.com/airbone4/home2026.git

## 在codespace 中,我們需要的git 指令


推
- git add . 
  - git 就是通知git 軟體吃後面的指令, 加入所有有關目前子目錄的改變
- git commit -m "訊息"
- git push

拉

- git pull



> 問題: 當我打 git commit -m "demo from 教室上的機器" 顯示如下的訊息
> Author identity unknown
>
>*** Please tell me who you are.
>
>Run
>
>  git config --global user.email "you@example.com"
>  git config --global user.name "Your Name"
>
> to set your account's default identity.
> Omit --global to set the identity only in this repository.
>
> fatal: unable to auto-detect email address (got 'user@DESKTOP-LH2N1MN.(none)')

git config user.email "linchao@nkust.edu.tw"

git config user.name "linchao"