## Docker Build Proxy Configuration

- When building Docker images on the host machine, you need to set up proxy settings in the terminal:
  ```
  export https_proxy=http://127.0.0.1:7897
  export http_proxy=http://127.0.0.1:7897
  ```
- These proxy settings (using port 7897) are necessary to resolve network issues during Docker image construction
- This configuration is specifically for building on the host machine
- The proxy points to localhost (127.0.0.1) on port 7897 of the development Linux machine

## Project Module Integration Guidelines

- When working on the ide-module, even if only debugging is requested, you must follow the hello-module directory's module integration guidelines
- Do not arbitrarily modify or implement the module outside of these guidelines
- The ide-module is an experimental module intended for potential future integration into the hello-HTML project
- Strict adherence to the established integration process is crucial for maintaining project consistency and experimental integrity