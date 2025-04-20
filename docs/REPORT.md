# 📄 Challenge Report

## Challenges Encountered & How I Addressed Them

This section highlights the main technical and architectural challenges I encountered while developing the NASA ETL
pipeline, along with the strategies and solutions I used to overcome them.

---

## 1. 🧪 Local Glue Simulation Was Too Fragile

**Problem:**  
I initially attempted to simulate AWS Glue locally using Docker (Spark + MinIO), aiming to develop and debug
transformation scripts in a cloudless environment. However, schema inference, file system permissions, and the lack of
Glue-specific features like Crawlers made the local environment unstable and unproductive.

**Solution:**  
I migrated transformation and enrichment logic to AWS Glue Jobs using real S3 buckets and Crawlers, significantly
improving reliability. I adopted a hybrid workflow: local prototyping → real Glue execution. Later on I managed to run
Glue interactively with PySpark locally which improved the development experience a lot.

---

## 2. 📦 AWS Glue Crawlers Failing Schema Inference

**Problem:**  
Glue Crawlers were generating invalid or nested schemas for some of the raw JSON data, especially for the NeoWs API,
which returns arrays under `near_earth_objects`.

**Solution:**  
I changed the extraction logic to write newline-delimited JSON (NDJSON), then used `explode()` in PySpark to normalize
arrays and nested objects. This made schema inference deterministic and
compatible with later transformation steps.

---

## 3. 🖼️ Enrichment Microservice Timeouts

**Problem:**  
When processing images from APOD or Mars Rover datasets, the enrichment microservice (running on
Lightsail) was taking too long to respond, mostly because of the low-spec free-tier instance that was struggling with
PyTorch classification and image processing. This was leading to longer-than-expected Glue job execution times.

**Solution:**

- Added timeouts to the enrichment jobs to prevent indefinite waiting.
- If reprocessing is necessary it can be made because images are also stored in S3 raw bucket.

---

## 4. 🌐 CORS Errors Prevented Frontend Image Rendering

**Problem:**
Initially, I attempted to render mosaic tiles directly from the original NASA image URLs. However, due to browser
security policies and missing CORS headers, images could not be loaded into the `<canvas>` from localhost or other
frontend environments.

**Solution:**

- Using Terraform, I applied a bucket policy and a CORS configuration to the bronze bucket that safely exposed only
  necessary image assets.
- In the frontend, I converted s3:// paths into public HTTP URLs dynamically. This allowed secure, performant image
  rendering without modifying backend APIs.

---

## ✅ Outcome

Despite the challenges, I successfully built and deployed a robust, modular ETL pipeline that automates data collection,
cleansing, enrichment, and loading from multiple NASA sources. All issues were addressed with production-oriented
solutions, and most were adapted into reusable Terraform modules and scalable job definitions.
