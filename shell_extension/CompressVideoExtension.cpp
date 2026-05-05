#include <windows.h>
#include <shobjidl.h>
#include <shlwapi.h>
#include <string>

#pragma comment(lib, "shlwapi.lib")
#pragma comment(lib, "ole32.lib")
#pragma comment(lib, "shell32.lib")
#pragma comment(lib, "advapi32.lib")

// {D4A8C520-E1C2-4F3E-9B7A-4A8D6C3E5F21}
static const CLSID CLSID_CompressVideo =
    {0xD4A8C520, 0xE1C2, 0x4F3E, {0x9B, 0x7A, 0x4A, 0x8D, 0x6C, 0x3E, 0x5F, 0x21}};

static LONG g_cRef = 0;

static std::wstring FindAppExe() {
    HKEY hKey;
    WCHAR path[MAX_PATH] = {};

    if (RegOpenKeyExW(HKEY_LOCAL_MACHINE,
        L"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\"
        L"{E8B6B4E5-2A59-4A6E-9D37-0D2F1B5D9B9F}_is1",
        0, KEY_READ, &hKey) == ERROR_SUCCESS) {
        DWORD size = sizeof(path);
        if (RegQueryValueExW(hKey, L"InstallLocation", NULL, NULL, (LPBYTE)path, &size) == ERROR_SUCCESS && path[0]) {
            std::wstring exe = std::wstring(path) + L"app.exe";
            RegCloseKey(hKey);
            if (GetFileAttributesW(exe.c_str()) != INVALID_FILE_ATTRIBUTES)
                return exe;
        }
        RegCloseKey(hKey);
    }

    LPCWSTR fallbacks[] = { L"C:\\Program Files\\Compress to 9MB\\app.exe" };
    for (auto p : fallbacks)
        if (GetFileAttributesW(p) != INVALID_FILE_ATTRIBUTES)
            return p;

    return L"";
}

class CompressVideoCommand : public IExplorerCommand {
    LONG m_cRef;
public:
    CompressVideoCommand() : m_cRef(1) { InterlockedIncrement(&g_cRef); }
    ~CompressVideoCommand() { InterlockedDecrement(&g_cRef); }

    // IUnknown
    STDMETHODIMP QueryInterface(REFIID riid, void **ppv) {
        if (!ppv) return E_POINTER;
        if (riid == IID_IUnknown || riid == IID_IExplorerCommand) {
            *ppv = static_cast<IExplorerCommand*>(this);
            AddRef();
            return S_OK;
        }
        *ppv = NULL;
        return E_NOINTERFACE;
    }
    STDMETHODIMP_(ULONG) AddRef() { return InterlockedIncrement(&m_cRef); }
    STDMETHODIMP_(ULONG) Release() {
        ULONG c = InterlockedDecrement(&m_cRef);
        if (c == 0) delete this;
        return c;
    }

    // IExplorerCommand
    STDMETHODIMP GetTitle(IShellItemArray*, LPWSTR* ppszName) {
        return SHStrDupW(L"Compress to ~9MB", ppszName);
    }

    STDMETHODIMP GetIcon(IShellItemArray*, LPWSTR* ppszIcon) {
        std::wstring exe = FindAppExe();
        return exe.empty() ? E_FAIL : SHStrDupW(exe.c_str(), ppszIcon);
    }

    STDMETHODIMP GetToolTip(IShellItemArray*, LPWSTR* ppszTip) {
        return SHStrDupW(L"Compress video to ~9MB for Discord", ppszTip);
    }

    STDMETHODIMP GetCanonicalName(GUID* pguid) {
        if (!pguid) return E_POINTER;
        *pguid = CLSID_CompressVideo;
        return S_OK;
    }

    STDMETHODIMP GetState(IShellItemArray*, BOOL, EXPCMDSTATE* pState) {
        if (!pState) return E_POINTER;
        *pState = ECS_ENABLED;
        return S_OK;
    }

    STDMETHODIMP Invoke(IShellItemArray* psiArray, IBindCtx*) {
        if (!psiArray) return S_OK;
        DWORD count = 0;
        psiArray->GetCount(&count);
        if (count == 0) return S_OK;

        IShellItem* pItem = NULL;
        if (FAILED(psiArray->GetItemAt(0, &pItem)) || !pItem) return S_OK;

        LPWSTR pName = NULL;
        if (SUCCEEDED(pItem->GetDisplayName(SIGDN_FILESYSPATH, &pName)) && pName) {
            std::wstring exe = FindAppExe();
            if (!exe.empty()) {
                std::wstring args = L"\"" + std::wstring(pName) + L"\"";
                ShellExecuteW(NULL, L"open", exe.c_str(), args.c_str(), NULL, SW_SHOWNORMAL);
            }
            CoTaskMemFree(pName);
        }
        pItem->Release();
        return S_OK;
    }

    STDMETHODIMP GetFlags(EXPCMDFLAGS* pFlags) {
        if (!pFlags) return E_POINTER;
        *pFlags = ECF_DEFAULT;
        return S_OK;
    }

    STDMETHODIMP EnumSubCommands(IEnumExplorerCommand**) { return E_NOTIMPL; }
};

class CFactory : public IClassFactory {
    LONG m_cRef;
public:
    CFactory() : m_cRef(1) {}

    STDMETHODIMP QueryInterface(REFIID riid, void **ppv) {
        if (!ppv) return E_POINTER;
        if (riid == IID_IUnknown || riid == IID_IClassFactory) {
            *ppv = static_cast<IClassFactory*>(this);
            AddRef();
            return S_OK;
        }
        *ppv = NULL;
        return E_NOINTERFACE;
    }
    STDMETHODIMP_(ULONG) AddRef() { return InterlockedIncrement(&m_cRef); }
    STDMETHODIMP_(ULONG) Release() {
        ULONG c = InterlockedDecrement(&m_cRef);
        if (c == 0) delete this;
        return c;
    }

    STDMETHODIMP CreateInstance(IUnknown* pOuter, REFIID riid, void** ppv) {
        if (pOuter) return CLASS_E_NOAGGREGATION;
        if (!ppv) return E_POINTER;
        CompressVideoCommand* p = new (std::nothrow) CompressVideoCommand();
        if (!p) return E_OUTOFMEMORY;
        HRESULT hr = p->QueryInterface(riid, ppv);
        p->Release();
        return hr;
    }
    STDMETHODIMP LockServer(BOOL) { return S_OK; }
};

// DLL exports
STDAPI DllGetClassObject(REFCLSID rclsid, REFIID riid, void** ppv) {
    if (rclsid != CLSID_CompressVideo) return CLASS_E_CLASSNOTAVAILABLE;
    if (!ppv) return E_POINTER;
    CFactory* p = new (std::nothrow) CFactory();
    if (!p) return E_OUTOFMEMORY;
    HRESULT hr = p->QueryInterface(riid, ppv);
    p->Release();
    return hr;
}

STDAPI DllCanUnloadNow() {
    return (g_cRef == 0) ? S_OK : S_FALSE;
}

BOOL APIENTRY DllMain(HMODULE hModule, DWORD reason, LPVOID) {
    (void)hModule;
    if (reason == DLL_PROCESS_DETACH && g_cRef != 0) {
        // Cleanup on forced unload
    }
    return TRUE;
}
