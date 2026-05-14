# Configuração do Provider AWS
provider "aws" {
  region = "us-east-1"
}

# Definição do Cluster EKS (Elastic Kubernetes Service)
resource "aws_eks_cluster" "aiops_cluster" {
  name     = "aiops-enterprise-cluster"
  role_arn = aws_iam_role.eks_cluster_role.arn

  vpc_config {
    # Em produção, estas seriam variáveis (vars)
    subnet_ids = ["subnet-12345abc", "subnet-67890def"]
  }

  depends_on = [
    aws_iam_role_policy_attachment.eks_cluster_policy
  ]
}

# Role IAM para o Cluster (Segurança)
resource "aws_iam_role" "eks_cluster_role" {
  name = "aiops-eks-cluster-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "eks.amazonaws.com"
        }
      },
    ]
  })
}

resource "aws_iam_role_policy_attachment" "eks_cluster_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
  role       = aws_iam_role.eks_cluster_role.name
}