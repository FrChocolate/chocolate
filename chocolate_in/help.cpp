#include <fstream>
#include <iostream>
#include <regex>
#include <sstream>
#include <string>

// ANSI Escape Sequences for terminal styling
const std::string RESET = "\033[0m";
const std::string BOLD = "\033[1m";
const std::string RED = "\033[31m";
const std::string YELLOW = "\033[33m";
const std::string BLUE = "\033[34m";
const std::string MAGENTA = "\033[35m";
const std::string UNDERLINE = "\033[4m";

// Function to replace markers with ANSI escape sequences
std::string applyStyles(const std::string &line) {
  std::string result = line;

  // Replace [red] with red color
  result = std::regex_replace(result, std::regex(R"(\[red\])"), RED);
  result = std::regex_replace(result, std::regex(R"(\[/red\])"), RESET);
  result =
      std::regex_replace(result, std::regex(R"(\[underline\])"), UNDERLINE);
  result = std::regex_replace(result, std::regex(R"(\[/underline\])"), RESET);

  // Replace [bold] with bold text
  result = std::regex_replace(result, std::regex(R"(\[bold\])"), BOLD);
  result = std::regex_replace(result, std::regex(R"(\[/bold\])"), RESET);

  // Replace [yellow] with yellow color
  result = std::regex_replace(result, std::regex(R"(\[yellow\])"), YELLOW);
  result = std::regex_replace(result, std::regex(R"(\[/yellow\])"), RESET);

  // Replace [blue] with blue color
  result = std::regex_replace(result, std::regex(R"(\[blue\])"), BLUE);
  result = std::regex_replace(result, std::regex(R"(\[/blue\])"), RESET);

  // Replace [magenta] with magenta color
  result = std::regex_replace(result, std::regex(R"(\[magenta\])"), MAGENTA);
  result = std::regex_replace(result, std::regex(R"(\[/magenta\])"), RESET);

  // Replace text inside backticks with blue color
  result = std::regex_replace(result, std::regex(R"(`([^`]+)`)"),
                              BLUE + "`$1`" + RESET);

  // Replace lines starting with - with 
  result = std::regex_replace(result, std::regex(R"(^\s*- )"), " ");

  return result;
}

// Function to display the help content
void displayHelp(const std::string &action) {
  std::ifstream file("/usr/share/doc/chocolate/" + action + ".txt");

  if (!file.is_open()) {
    std::cerr << "Help file for '" << action << "' not found.\n";
    return;
  }

  std::string line;
  while (std::getline(file, line)) {
    std::cout << applyStyles(line) << "\n";
  }

  file.close();
}

int main(int argc, char *argv[]) {
  if (argc != 2) {
    std::cerr << "Usage: " << argv[0] << " <command_name>\n";
    return 1;
  }

  std::string command = argv[1];
  displayHelp(command);

  return 0;
}
