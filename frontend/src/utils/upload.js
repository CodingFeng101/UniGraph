export const MAX_FILE_SIZE = 50 * 1024 * 1024;
export const MAX_IMAGE_SIZE = 5 * 1024 * 1024;

export function validateUploadSize(file, maxSize = MAX_FILE_SIZE) {
  if (!file || file.size <= maxSize) return;
  throw new Error(`“${file.name}”不能超过 ${maxSize / 1024 / 1024} MB`);
}

export function validateUploadFiles(files, maxSize = MAX_FILE_SIZE) {
  Array.from(files || []).forEach(function(file) {
    validateUploadSize(file, maxSize);
  });
}
