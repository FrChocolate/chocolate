#include <cstdlib>
#include <fstream>
#include <iostream>
#include <sched.h>
#include <signal.h>
#include <string>
#include <sys/mount.h>
#include <sys/resource.h>
#include <sys/wait.h>
#include <unistd.h>

#define STACK_SIZE (1024 * 1024)

// Colors
#define RESET "\033[0m"
#define RED "\033[31m"
#define GREEN "\033[32m"
#define YELLOW "\033[33m"
#define BLUE "\033[34m"
#define MAGENTA "\033[35m"

void set_resource_limits(int max_memory, int max_cpu) {
  if (max_memory != -1) {
    struct rlimit mem_limit;
    mem_limit.rlim_cur = mem_limit.rlim_max =
        max_memory * 1024 * 1024; // In bytes
    setrlimit(RLIMIT_AS, &mem_limit);
    std::cout << GREEN << "Memory limit set to " << max_memory << "MB" << RESET
              << std::endl;
  }

  if (max_cpu != -1) {
    struct rlimit cpu_limit;
    cpu_limit.rlim_cur = cpu_limit.rlim_max = max_cpu;
    setrlimit(RLIMIT_CPU, &cpu_limit);
    std::cout << GREEN << "CPU time limit set to " << max_cpu << " seconds"
              << RESET << std::endl;
  }
}

void set_cpu_freq(int freq) {
  if (freq == -1)
    return;

  std::ofstream cpu_min(
      "/sys/devices/system/cpu/cpu0/cpufreq/scaling_min_freq"); // check for cpu
                                                                // min freq
  std::ofstream cpu_max(
      "/sys/devices/system/cpu/cpu0/cpufreq/scaling_max_freq"); // check for cpu
                                                                // max freq

  if (cpu_min.is_open() && cpu_max.is_open()) {
    cpu_min << freq * 1000; // Convert to kHz
    cpu_max << freq * 1000;
    std::cout << BLUE << "CPU frequency set to " << freq << " MHz" << RESET
              << std::endl;
  } else {
    std::cerr << RED << "Failed to set CPU frequency" << RESET << std::endl;
    exit(1);
  }
}

int child(void *arg) {
  char **args = static_cast<char **>(arg);
  std::string command = args[0];
  int max_memory = std::stoi(args[1]);
  int max_cpu = std::stoi(args[2]);
  int cpu_freq = std::stoi(args[3]);

  // Set limits
  std::cout << YELLOW << "Setting resource limits..." << RESET << std::endl;
  set_resource_limits(max_memory, max_cpu);
  set_cpu_freq(cpu_freq);

  // Mount filesystem for process isolation
  std::cout << YELLOW << "Mounting filesystem for process isolation..." << RESET
            << std::endl;
  mount("none", "/", NULL, MS_REC | MS_PRIVATE, NULL);

  // Run command
  std::cout << MAGENTA << "Executing command: " << command << RESET
            << std::endl;
  if (system(command.c_str()) < 0) {
    std::cerr << RED << "Failed to execute command" << RESET << std::endl;
    exit(1);
  }

  return 0;
}

int main(int argc, char *argv[]) {
  if (argc < 5) {
    std::cerr << RED
              << "Usage: ./sandbox <command> <memory_MB> <cpu_time_sec> "
                 "<cpu_freq_MHz>"
              << RESET << std::endl;
    return 1;
  }

  // Allocate stack
  std::cout << YELLOW << "Allocating stack for child process..." << RESET
            << std::endl;
  char *stack = static_cast<char *>(malloc(STACK_SIZE));
  if (!stack) {
    std::cerr << RED << "Memory allocation failed" << RESET << std::endl;
    return 1;
  }

  // Clone process
  std::cout << YELLOW << "Cloning process..." << RESET << std::endl;
  pid_t pid = clone(child, stack + STACK_SIZE,
                    CLONE_NEWPID | CLONE_NEWNS | SIGCHLD, argv + 1);

  if (pid < 0) {
    std::cerr << RED << "Clone failed" << RESET << std::endl;
    free(stack);
    return 1;
  }

  int status;
  waitpid(pid, &status, 0);

  if (WIFEXITED(status)) {
    std::cout << GREEN
              << "Child process exited with status: " << WEXITSTATUS(status)
              << RESET << "\n";
  } else if (WIFSIGNALED(status)) {
    std::cout << RED
              << "Child process was killed by signal: " << WTERMSIG(status)
              << RESET << "\n";
  }

  free(stack);
  return 0;
}
