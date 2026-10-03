// Compile the real PI implementation; discard unrelated ROM functions at link.
#include <cassert>
#include <iterator>
#include "pi.cpp"

std::filesystem::path config_path;
std::atomic_bool exited{true};

int main(int argc, char** argv) {
    assert(argc == 2);
    const std::filesystem::path directory = argv[1];
    std::filesystem::create_directories(directory);

    // Quitting before game initialization must not create any save.
    assert(ultramodern::join_saving_thread());
    assert(std::filesystem::is_empty(directory));
    save_context.save_file_path = directory / "eeprom.bin";
    save_context.save_buffer.resize(get_save_size(recomp::SaveType::Eep4k));
    assert(save_context.save_buffer.size() == 512);
    std::vector<char> expected(512);
    for (size_t i = 0; i < expected.size(); ++i) {
        expected[i] = static_cast<char>(i ^ 0x5a);
    }

    // An accepted write is still pending when exited skips the async saver.
    save_write_ptr(expected.data(), 0, expected.size());
    save_context.saving_thread = std::thread(saving_thread_func, nullptr);
    assert(ultramodern::join_saving_thread());
    std::ifstream saved(save_context.save_file_path, std::ios::binary);
    const std::vector<char> actual{std::istreambuf_iterator<char>(saved), {}};
    assert(actual == expected);
    saved.close();

    // Reload through the real native reader, not a second parser.
    std::fill(save_context.save_buffer.begin(), save_context.save_buffer.end(), 0);
    read_save_file();
    assert(save_context.save_buffer == expected);

    // Final persistence cannot report success for an unwritable destination.
    save_context.save_file_path = directory / "missing" / "eeprom.bin";
    save_context.saving_thread = std::thread(saving_thread_func, nullptr);
    assert(!ultramodern::join_saving_thread());
    assert(!std::filesystem::exists(save_context.save_file_path));

    // Exercise a write/close error after a successful open. files.cpp owns the
    // .temp suffix; /dev/full is the Linux kernel's deterministic ENOSPC sink.
    save_context.save_file_path = directory / "eeprom.bin";
    std::filesystem::create_symlink("/dev/full", directory / "eeprom.bin.temp");
    std::fill(save_context.save_buffer.begin(), save_context.save_buffer.end(), 0x33);
    save_context.saving_thread = std::thread(saving_thread_func, nullptr);
    assert(!ultramodern::join_saving_thread());
    std::ifstream unchanged(save_context.save_file_path, std::ios::binary);
    const std::vector<char> preserved{std::istreambuf_iterator<char>(unchanged), {}};
    assert(preserved == expected);
    puts("EEPROM checks passed: pre-init exit, pending 512-byte write, native reload and failed open/write preservation");
}
