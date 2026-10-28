# Statement Extractor — Bank Statement Table Extraction & Banking Analytics Dashboard

[![Production Backend](https://img.shields.io/badge/Production%20Backend-READY%20(200%20OK)-teal.svg)](https://mayank-ten-indol.vercel.app/health)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-blue.svg)](https://www.typescriptlang.org/)
[![React](https://img.shields.io/badge/React-19-cyan.svg)](https://react.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind%20CSS-v4-38bdf8.svg)](https://tailwindcss.com/)
[![Vitest](https://img.shields.io/badge/Vitest-32%2F32%20Passing-emerald.svg)](https://vitest.dev/)
[![Oxlint](https://img.shields.io/badge/Oxlint-0%20Warnings-success.svg)](https://oxc.rs/)

A single-page fintech application recreating the Statement Extractor dashboard design and connecting directly to the deployed Bank Muscat BRD Series FastAPI backend.

---

## Design System Specifications

| Element | Specification | Hex / Implementation |
| :--- | :--- | :--- |
| **UI Font** | **IBM Plex Sans** (Google Fonts) | Weights 400, 500, 600, 700 |
| **Number Font** | **IBM Plex Mono** (Google Fonts) | Tabular figures (`tabular-nums`) |
| **Page Background** | Soft Slate | `#F3F6F9` |
| **Cards** | Clean White | `#FFFFFF`, border 1px `#DDE3EA`, radius `14px` |
| **Header & Primary Text** | Navy | `#0B2545` |
| **Muted Text** | Slate Muted | `#55657A` |
| **Teal Accent / Primary CTA** | Solid Teal | `#0E7C86` (hover `#0B6B74`) |
| **Light Teal Background** | Soft Aqua | `#E3F4F5` |
| **Credits (Income)** | Emerald Green | `#0B7A4B` |
| **Debits (Outflow)** | Ruby Red | `#B42318` |
| **Needs Review Card / Badge** | Amber Review | Bg `#FFF8E6`, Border `#F0D58C`, Text `#6B4200` |
| **Layout Dimensions** | Maximum Width | `1344px`, 24px grid gaps, responsive touch targets &ge; 44px |

### Category Chip Styling

- **Income**: Bg `#DDF3E8`, Text `#0B6B43`
- **Groceries**: Bg `#E3EEFB`, Text `#1F4E8C` (Chart: `#2F6FD0`)
- **Utilities**: Bg `#FFF1D6`, Text `#7A4A00` (Chart: `#E0A100`)
- **Transport**: Bg `#E8E4FA`, Text `#4B3A9A` (Chart: `#8E6CE0`)
- **Cash**: Bg `#EDEFF2`, Text `#3B4656` (Chart: `#3B4656`)
- **Transfers**: Bg `#D9F1F3`, Text `#0B6169` (Chart: `#0E7C86`)
- **Dining**: Bg `#FBE3EC`, Text `#9B1C4B` (Chart: `#D6336C`)
- **Fallback / Other**: Bg `#EDEFF2`, Text `#55657A` (Chart: `#8A99AD`)

---

## Architecture & Technology Stack

- **Framework**: React 19 + Vite 8 + TypeScript 5
- **Styling**: Tailwind CSS v4 with custom fintech tokens
- **Data Fetching**: TanStack Query v5 (30s health polling) + Axios client (60s timeout, granular CORS error normalizer)
- **Visualizations**: Recharts (Donut chart with centered total, Area chart with gradient fill and tabular mono ticks)
- **Document Rendering**: `react-pdf` (pdf.js worker) with zoom controls and dashed table overlay
- **Spreadsheet Generation**: SheetJS (`xlsx`) for multi-format export
- **Testing & Linter**: Vitest (32 passing unit tests), Oxlint (0 warnings)

---

## Backend Integration & Data Contract

### Target Endpoints
- Base URL: `https://mayank-ten-indol.vercel.app` (Canonical warmed production alias)
- Fallback Base URL: `http://127.0.0.1:8000` (Local FastAPI server)
- `GET /health`: Returns service health status, ML line classifier, NLP categorizer, and supported profiles count.
- `GET /profiles`: Returns supported bank profile schemas and date/currency configurations.
- `POST /extract`: Multipart file upload returning structured tables, accounts, and running-balance validation.
- `POST /categorize`: JSON payload `{"descriptions": string[], "use_transformers": boolean}` returning categorized narratives and confidence scores.
- `GET /docs`: Swagger UI documentation.

### Data Mapping Contract
Backend transaction responses are mapped directly into the UI `Row` type:
```typescript
export interface Row {
  id: string
  date: string
  description: string
  debit: number | null
  credit: number | null
  balance: number | null
  category?: string | null
  confidence?: number | null
  needsReview?: boolean
}
```

---

## Bundled Sample Statement Specification

The dashboard bundles the exact synthetic Bank Muscat statement from the reference specification:
- **File**: `statement_sep_2026.pdf` (2 pages, 184 KB, Profile: Auto-detect, 98.2% confidence)
- **Total Credits**: `2,100.000 OMR` (2 transactions: Salary credit `1,850.000` + Transfer `250.000`)
- **Total Debits**: `210.000 OMR` (6 transactions: Lulu `42.350`, Omantel `18.000`, Shell `12.500`, ATM `100.000`, Talabat `9.750`, Electricity `27.400`)
- **Net Flow**: `+1,890.000 OMR` (Opening `1,562.450` &rarr; Closing `3,452.450`)
- **Needs Review**: 1 row (`Talabat food order`, amount `9.750 OMR`, flagged with amber badge and row highlight)

---

## Quickstart Guide

### 1. Installation
```powershell
cd frontend
npm install
```

### 2. Run Development Server
```powershell
npm run dev
```
Open [http://127.0.0.1:5173](http://127.0.0.1:5173).

### 3. Run Unit Tests
```powershell
npm run test
```
Executes all 32 Vitest unit tests verifying currency decimals, date parsing, balance reconciliation, CSV escaping, and demo fixture accuracy.

### 4. Run Code Linter
```powershell
npm run lint
```
Executes Oxlint across all 55 source files with zero warnings and zero errors.

### 5. Production Build
```powershell
npm run build
```
Generates production assets in `frontend/dist/` with zero TypeScript or bundling errors.
