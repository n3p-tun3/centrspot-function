# Keyword Video Frame Generator - Appwrite Function

This Appwrite Function generates PNG frames with a keyword highlighting effect for video generation.

## Setup Instructions

### 1. Create Storage Bucket

In your Appwrite Console:
1. Go to Storage
2. Create a new bucket named `frames`
3. Set permissions:
   - Read access: `any` (or specific users)
   - Create/Update/Delete: None (only function can write)
4. Set file security to enabled
5. Optional: Set TTL (Time To Live) to auto-delete frames after 1 hour

### 2. Deploy Function

```bash
# Install Appwrite CLI
npm install -g appwrite

# Login to your Appwrite instance
appwrite login

# Initialize project (if not already done)
appwrite init project

# Deploy function
appwrite deploy function

# Or manually create function in console and upload files
```

### 3. Configure Environment Variables

In Appwrite Console → Functions → Your Function → Settings:
- `BUCKET_ID`: `frames` (or your bucket name)

The following are automatically provided by Appwrite:
- `APPWRITE_FUNCTION_API_ENDPOINT`
- `APPWRITE_FUNCTION_PROJECT_ID`

### 4. Set Function Permissions

- Execute permissions: `any` (or authenticated users only)
- Timeout: 30 seconds (should be enough for 7 frames)

## API Usage

### Request

**Endpoint:** `POST /functions/[FUNCTION_ID]/executions`

**Headers:**
```
Content-Type: application/json
X-Appwrite-Project: [YOUR_PROJECT_ID]
```

**Body:**
```json
{
  "keyword": "Hello World",
  "highlight": true,
  "frame_count": 7
}
```

**Parameters:**
- `keyword` (string, required): Text to highlight (1-50 characters)
- `highlight` (boolean, optional): Show highlight box behind keyword (default: true)
- `frame_count` (integer, optional): Number of frames to generate (1-20, default: 7)

### Response

**Success (200):**
```json
{
  "success": true,
  "frames": [
    {
      "id": "frame_123456_000",
      "url": "https://[ENDPOINT]/storage/buckets/frames/files/frame_123456_000/view?project=[PROJECT_ID]",
      "index": 0
    },
    ...
  ],
  "frame_count": 7,
  "keyword": "Hello World",
  "highlight": true
}
```

**Error (400/500):**
```json
{
  "success": false,
  "error": "Error message"
}
```

## Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Test locally (you'll need to mock the context object)
python main.py
```

## Frame Specifications

- **Resolution:** 1080×1920 (vertical/portrait)
- **Format:** PNG
- **Background:** Cream (#F5F2EB)
- **Keyword Color:** Yellow highlight (#FFE678)
- **Text:** Randomized surrounding text with fade effect

## Notes

- Frames are stored in Appwrite Storage with unique IDs
- Each frame is ~200-400KB
- Consider setting up automatic cleanup (TTL) for storage
- Function timeout should be sufficient for up to 20 frames
