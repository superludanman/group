## Docker Build Proxy Configuration

- When building Docker images on the host machine, you need to set up proxy settings in the terminal:
  ```
  export https_proxy=http://127.0.0.1:7897
  export http_proxy=http://127.0.0.1:7897
  ```
- These proxy settings (using port 7897) are necessary to resolve network issues during Docker image construction
- This configuration is specifically for building on the host machine
- The proxy points to localhost (127.0.0.1) on port 7897 of the development Linux machine