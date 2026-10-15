# 茨城県公立図書館データベース データ構造設計指針

## 1. 施設単位の独立データ管理 (Facility-Level Independence)

### 永続的施設ID体系 (Persistent Facility ID)
- 形式: `IB-{JIS自治体コード5桁}-{施設連番2桁}`
  - 例: `IB-08201-01` (水戸市立中央図書館), `IB-08203-02` (土浦市立図書館 三中地区分館)
- 自治体合併や統廃合が発生した場合でも、旧施設のIDは破棄せず `status: closed` または `status: merged` として永続化する。
- 各施設エンティティは以下の独立メタデータを必須とする:
  - `facility_id`: 永続的一意ID
  - `name`: 施設正式名称
  - `category`: 収録対象区分 (Cat A / Cat B / Cat C / Cat D)
  - `legal_status`: 法規上の位置づけ
  - `history`: 沿革・改称・移転・統廃合のタイムライン配列
  - `sources`: 参照した情報源IDリスト (`SRC-XXXX`)
  - `verification`: 個別検証状態 (`status`, `verified_at`, `scope`)

## 2. 統計の集計単位と二重計上防止 (Statistical Aggregation & Deduplication)

### 集計単位の厳格分離
- **`facility_level` (単館統計)**: 特定の施設単体に直接帰属する数値 (座席数、開架冊数、単館受入数など)
- **`system_aggregate` (システム全体統計)**: 自治体内の全館合計または相互利用ネットワーク全体で集計された数値 (共通利用カード登録者数、全館貸出総数、移動図書館合算など)

### 二重計上防止ルール
- 統計ブロックに `scope` (`facility_level` | `system_aggregate`) および `aggregation_type` (`measured` | `sum_total`) を明示する。
- 派生データ出力 (CSV, GeoJSON, Webサイト) の集計処理では、`scope == "facility_level"` のみを積み上げ、`system_aggregate` との突き合わせ検算を行う。

## 3. 収録対象の分類と網羅性区分 (Target Coverage & Taxonomy)

- **Category A (図書館法本則施設)**:
  - 図書館法第2条に基づく公立図書館の本館・分館・地区館。
- **Category B (法規指定分室・文庫)**:
  - 図書館条例や施行規則に直接明記された分室、配本所、文庫。
- **Category C (公民館図書室・教育集落拠点)**:
  - 社会教育法第21条に基づく公民館図書室・地域交流センター図書室 (県図書館協会加盟施設または常設窓口)。
- **Category D (未調査・未確認拠点)**:
  - 自治体内に存在する可能性のある小規模配本所、学校図書室一般開放窓口等のうち、一次資料照合が未完了の拠点。
