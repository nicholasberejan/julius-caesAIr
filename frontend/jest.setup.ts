import "@testing-library/jest-dom";

const ensureRandomUUID = () => {
  if (!globalThis.crypto) {
    Object.defineProperty(globalThis, "crypto", {
      value: {},
      writable: false,
    });
  }

  if (!globalThis.crypto.randomUUID) {
    Object.defineProperty(globalThis.crypto, "randomUUID", {
      value: () => "test-uuid",
      writable: false,
    });
  }
};

ensureRandomUUID();
