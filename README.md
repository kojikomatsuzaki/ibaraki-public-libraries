# 茨城県公立図書館データベース (Ibaraki Public Libraries Open Database)

茨城県内全44市町村の公立図書館（本館・分館・地区館・分室・文庫）および主要公民館図書室（計100拠点）を一次資料（条例・施行規則・要覧・茨城県図書館協会統計）から照合したオープンデータベース（Single Source of Truth）です。

## 編纂・著作者
- **小松崎 浩司** (Koji Komatsuzaki)
- 共同開発・監査パートナー: Google Gemini

## ディレクトリ構成
- `data/libraries/`: 全44市町村のCanonical YAMLデータ（`08201_mito.yaml` 〜 `08564_tone.yaml`）
- `data/sources/`: 一次資料の書誌・検証メタデータ（`SRC-0001.yaml` 〜 `SRC-0019.yaml`）
- `data/municipalities/`: 44市町村マスター（`master_municipalities.json`）、3ピラー監査台帳（`audit_registry.json`）、進捗状態（`progress_state.json`）
- `data/history/`: データ監査・更新前後の差分パッチ記録
- `scripts/validate/`: 自動検証スクリプト群（`audit_validator.py`, `canonical_data_validator.py`, `verify_cross_reference.py`）
- `scripts/build/`: Canonical YAMLから公開用JSON/CSV/GeoJSONを生成するビルドスクリプト（`generate_site_data.py`）
- `docs/`: GitHub Pages公開用レスポンシブ・バイリンガルWebサイト（`index.html`, `data/`, `reports/`）

## 行動規範・運用原則
本プロジェクトにおける調査・ファクトチェック・出典管理および開発運用は、以下の規範に厳格に準拠して進められます。
- [エビデンスと参照資料の明示 (Evidence-Based Reporting and Cross-Referencing)](rules/evidence_based_reporting.md)
- [運用・開発原則 (Operational Principles)](rules/operational_principles.md)
- [データ構造設計指針 (Data Architecture)](rules/data_architecture.md)
- [独立監査および批判的再調査報告書](docs/reports/canonical_data_audit_report.md)

## ライセンス
- データ・解説・メタデータ: **CC BY 4.0 International**
- プログラムコード: **MIT License**
