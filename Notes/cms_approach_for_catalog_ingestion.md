# Catalogue Management System (CMS)
## Approach for Secure, Scalable, Multi-Tenant Catalog Ingestion

---

## 1. Objective

The objective is to design a **Catalogue Management System (CMS)** that can reliably store and manage **structured and unstructured product data** such as prices, specifications, images, and links. The CMS serves as the foundation for downstream systems (such as search or AI assistants) by converting raw catalogs into governed, queryable data.

---

## 2. High-Level Approach

My approach is to **separate concerns clearly**:

- The **CMS** focuses only on data ingestion, storage, and governance
- Intelligence layers (search, AI, chat) consume data from the CMS but do not manage it

This ensures the system is scalable, maintainable, and production-ready.

---

## 3. Multi-Tenant Design Strategy

The CMS is designed as a **multi-tenant system**, where each organization (tenant) has fully isolated data.

### Key decisions:
- Every entity (catalogs, PDFs, products, images) is associated with a `tenant_id`
- All database queries are scoped to a tenant
- Users can only access data belonging to their tenant

This design enables multiple customers to safely share the same infrastructure.

---

## 4. Data Storage Design

### 4.1 Unstructured Data (Files)

**What is stored**
- Catalog PDFs
- Images extracted from PDFs
- Related documents

**Storage approach**
- Files are stored in object storage
- The database stores only metadata and references to these files

This keeps the database lightweight and scalable.

---

### 4.2 Structured and Semi-Structured Data

**What is stored in the database**
- Tenant and catalog information
- PDF metadata (name, page count)
- Products and identifiers
- Prices and specifications
- Links and references
- Ingestion job status

A relational database is used as the **system of record** to ensure consistency and traceability.

---

## 5. Database Design Approach

The database schema is designed around clarity and traceability rather than complexity.

### Core entities:
- Tenant
- Catalog
- PDF Asset
- Product
- Product Version (for prices)
- Image Asset
- Ingestion Job

### Key rules:
- No binary files stored in the database
- All extracted data links back to the original PDF
- Prices and specs are versioned where needed

This makes it easy to audit and reprocess catalogs when required.

---

## 6. Ingestion Pipeline Design

Catalog ingestion is implemented as an **asynchronous pipeline**.

### Ingestion steps:
1. User uploads a catalog PDF
2. PDF is stored securely
3. An ingestion job is created
4. Text and tables are extracted
5. Images are extracted and stored
6. Extracted data is mapped into products, prices, and specs
7. Job status is updated with success or errors

Each step is tracked independently to support retries and debugging.

---

## 7. Security and Reliability Considerations

### Security
- Tenant-based access control
- Signed URLs for file access
- Role-based permissions

### Reliability
- Background processing for ingestion
- Idempotent ingestion jobs
- Error logging per ingestion step

These ensure the system is safe and dependable in production.

---

## 8. Why This Approach

This approach:
- Scales across multiple tenants and catalogs
- Keeps raw data and processed data clearly separated
- Makes downstream systems simpler and more reliable
- Avoids tight coupling between ingestion and intelligence layers

It focuses on building a **strong data foundation first**, which is critical for any advanced system built on top of catalogs.

---

## 9. Summary

The CMS is designed as a secure, multi-tenant platform that transforms raw catalog files into structured, governed data. By prioritizing clean data modeling, asynchronous ingestion, and tenant isolation, this approach ensures long-term scalability and correctness while remaining simple enough to evolve over time.

