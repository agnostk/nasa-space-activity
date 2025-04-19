resource "aws_db_instance" "postgresql" {
  identifier          = "${local.name-prefix}-postgres-db"
  engine              = "postgres"
  engine_version      = "17.2"
  instance_class      = "db.t3.micro"
  allocated_storage   = 20
  storage_type        = "gp2"
  username            = var.db_username
  password            = var.db_password
  db_name             = "nasa"
  skip_final_snapshot = true
  publicly_accessible = true
  deletion_protection = false
  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  multi_az            = false
}