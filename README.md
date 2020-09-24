cấu trúc thư mục của hệ thống:

-application chứa các api mà ứng dụng tương tác với giao diện người dùng

-cofig chứa các file cấu hình của hệ thống

-dataprocessing chứa các thành phần tiền xử lý dữ liệu

    +dataprocessing.crawler chứa thành phần crawl dữ liệu từ web lưu trữ trên hdfs và elasticsearch
    +dataprocessing.streaming sử dụng spark streaming để xử lý các dữ liệu được crawl về, xây dựng đồ thị tri thức 
-db_services chứa các thành phần tương tác với database gồm hdfs,neo4j và elasticsearch

-ER định nghĩa các lớp thực thể và quan hệ trên đồ thị tri thức

-frontend  chứa giao diện người dùng

-knowledge_graph chứa thành phần tương tác với đồ thị tri thức, sử dụng neo4j

-model chứa mô hình trích rút thực thể quan hệ từ văn bản.

file requirements.txt chứa các thư viện sử dụng trong project