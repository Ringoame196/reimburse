# reimburse（精算管理アプリ）

Python 標準ライブラリ（`http.server` / `sqlite3`）と Vanilla JavaScript + Bootstrap 5 で構築されたシンプルな精算データ管理 Web アプリケーションです。

## 機能概要

* **登録フォーム (`/form`)**: 精算内容・日付・金額の入力と新規登録
* **精算一覧 (`/view`)**: 登録済みデータのテーブル表示と合計金額の自動集計
* **管理画面 (`/manage`)**: 登録済みデータの確認（曜日付き日付表示）と個別削除

## ディレクトリ構成

```text
reimburse/
├── server.py          # HTTPサーバー & SQLiteデータベース操作 & REST API
├── expenses.db        # SQLiteデータベースファイル（初回起動時に自動生成）
├── form.html          # 精算登録画面
├── view.html          # 精算一覧画面
├── manage.html        # 精算管理（削除）画面
└── scripts/
    ├── form.js        # 登録フォームの送信・バリデーション処理
    ├── view.js        # 一覧データの取得・テーブル描画・合計計算処理
    └── manage.js      # 管理画面の描画・削除API連携処理
```

## 動作環境

* Python 3.10 以上（型ヒント `list[dict]` / `dict | None` 等を使用しているため）
* Git
* モダンブラウザ（Chrome / Edge / Firefox / Safari など）
* インターネット接続（Bootstrap 5 の CDN 読み込み用）

## 起動方法

1. リポジトリをクローンし、ディレクトリに移動します。

   ```bash
   git clone https://github.com/Ringoame196/reimburse.git
   cd reimburse
   ```

2. サーバーを起動します。初回起動時に `expenses.db` と `expenses` テーブルが自動作成されます。

   ```bash
   python server.py
   ```
   ※ Windows の PowerShell の場合は `python .\server.py` でも実行できます。

3. ブラウザで以下の URL にアクセスします。

   * 登録フォーム: `http://127.0.0.1:8000/form`
   * 精算一覧: `http://127.0.0.1:8000/view`
   * 管理画面: `http://127.0.0.1:8000/manage`

サーバーを停止する場合は、ターミナル上で `Ctrl + C` を押してください。

## データベース仕様 (`expenses.db`)

テーブル名: `expenses`

| カラム名 | 型 | 制約 | 説明 |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | `PRIMARY KEY AUTOINCREMENT` | 精算ID |
| `content` | `TEXT` | `NOT NULL` | 精算内容 |
| `date` | `TEXT` | `NOT NULL` | 日付 (`YYYY-MM-DD`) |
| `amount` | `INTEGER` | `NOT NULL` | 金額（1以上の整数） |

## API エンドポイント

| メソッド | パス | 説明 | リクエスト / レスポンス例 |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/expenses` | 精算一覧の取得（日付降順） | レスポンス `200`: `{"expenses": [{"id": 1, "content": "交通費", "date": "2026-11-27", "amount": 500}]}` |
| `POST` | `/api/expenses` | 精算データの新規登録 | リクエスト: `{"content": "交通費", "date": "2026-11-27", "amount": 500}`<br>レスポンス `201`: `{"status": "ok", "expense": {...}}` |
| `DELETE` | `/api/expenses/<id>` | 指定IDの精算データを削除 | レスポンス `200`: `{"status": "ok", "deleted_id": 1}` |