import sys
from awsglue.utils import getResolvedOptions
from awsglue.context import GlueContext
from pyspark.context import SparkContext
from pyspark.sql import functions as F

# Get parameters from Step Function
args = getResolvedOptions(sys.argv, ["JOB_NAME", "bucket", "key"])

bucket = args["bucket"]
key = args["key"]

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

# Input and output paths
input_path = f"s3://{bucket}/{key}"
output_path = "s3://final-buc1409/sales_curated/"

# Read sales CSV
df = spark.read.option("header", "true").csv(input_path)

# Transformations
# 1. Drop duplicates
df = df.dropDuplicates()

# 2. Handle nulls (example: fill missing Quantity/UnitPrice with 0)
df = df.fillna({"Quantity": 0, "UnitPrice": 0})

# 3. Cast numeric columns
df = df.withColumn("Quantity", F.col("Quantity").cast("int"))
df = df.withColumn("UnitPrice", F.col("UnitPrice").cast("double"))

# 4. Add TotalAmount column
df = df.withColumn("TotalAmount", F.col("Quantity") * F.col("UnitPrice"))

# 5. Convert OrderDate to proper date
df = df.withColumn("OrderDate", F.to_date("OrderDate", "yyyy-MM-dd"))

# 6. (Optional) filter invalid rows → save separately
valid_rows = df.filter(F.col("OrderID").isNotNull())
invalid_rows = df.filter(F.col("OrderID").isNull())

# Save valid rows to curated bucket (single CSV file)
valid_rows.coalesce(1).write.mode("overwrite").option("header", "true").csv(output_path)

# Save invalid rows for debugging
if invalid_rows.count() > 0:
    invalid_rows.write.mode("overwrite").option("header", "true").csv("s3://final-buc1409/sales_errors/")