# seo_startingbasics_checker

## このプログラムはなに？
 このプログラムは、与えられたウェブページ（サイト全体ではなくそのページのみ）が、Google検索に対するSEO対策で基本的な失敗をしていないかを10項目に渡ってチェックし、配点に基づき0～100点満点でのスコアを出力します。

## どう使うの？
このプログラムはPythonで動きます。Pythonと必要なライブラリ（後述）をインストールしてコマンドラインで Python の実行パラメーターとして本ソース "startingbasics.py" は実行されます。実行にあたっては、第一引数が必須です。第一引数として、診断を行いたいページの有効な URI を渡してください。採点理由と得点を順次表示しながら、診断をすすめてゆき、最後に総合得点0～100点を出力します。

## プログラムの限界
このプログラムは、Google検索のスコアリング基準において一般的かつ基本的最低限の診断チェックを行うツールです。
診断チェックにおいて満点が出ないサイトは、ウェブページとして論外な問題があります。採点基準をよく読んで、満点がとれるようにウェブページを改修してください。
診断によって満点が出たら、そこがスタートラインだと考えて下さい。基本が押さえられて、初めてGoogle検索は純粋なページの良し悪しをスコアリングしてくれます。
頑張って最高のウェブページを作って下さい。

## 注意！
かなり重要な注意です。
このプログラムは "9. インバウンドリンクのチェック" のプロセスにおいて、多くのGoogle検索APIを使用します。
あまり連続して使用すると、Googleに怒られたりまずいことになるかも知れません。

## 免責事項
本プログラムの使用によって起こる、不利益や損害、その他あらゆるトラブルに対して、プログラム開発者は責任を負いません。
 
 ## author
 Amano Hotori
