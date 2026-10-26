"""Browser observer and independent emitted-byte checks; no import side effects."""

BROWSER_JS = r"""const {createRequire}=require('node:module');
const fs=require('node:fs');const path=require('node:path');const crypto=require('node:crypto');
const requireWeb=createRequire(path.join(process.cwd(),'apps/workspace-web/package.json'));
const {chromium,expect}=requireWeb('@playwright/test');
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:path.join(process.env.LOCALAPPDATA,'ms-playwright/chromium-1234/chrome-win64/chrome.exe')});
 const context=await browser.newContext({viewport:{width:1366,height:900},acceptDownloads:true});
 await context.addInitScript(()=>{
  window.__proof={created:[],revoked:[],headers:[]};
  const create=URL.createObjectURL.bind(URL),revoke=URL.revokeObjectURL.bind(URL);
  URL.createObjectURL=(blob)=>{const url=create(blob);window.__proof.created.push(url);return url;};
  URL.revokeObjectURL=(url)=>{window.__proof.revoked.push(url);return revoke(url);};
  const fetchReal=window.fetch.bind(window);
  window.fetch=async(...args)=>{const r=await fetchReal(...args);if(String(args[0]).includes('/export?')&&r.ok)window.__proof.headers.push({disposition:r.headers.get('Content-Disposition'),mime:r.headers.get('Content-Type')});return r;};
 });
 const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
 const results=[];
 try{
  await page.goto(process.env.P5A_WEB);
  await page.fill('#username','sup1');await page.fill('#password','sup1-devpass');
  await page.click('button[type="submit"]');await page.waitForSelector('main.operations-console');
  await page.selectOption('#shift-select',process.env.P5A_SHIFT_ID);
  const panel=page.getByRole('region',{name:'End-shift report',exact:true});
  await expect(panel.getByRole('button',{name:'Download report version 2',exact:true})).toBeVisible();
  const cases=[];
  for(const view of ['shift-summary','customer-report','incident-report','handover-report'])for(const format of ['pdf','xlsx'])cases.push({version:2,id:process.env.P5A_REPORT_ID,view,format});
  for(const format of ['pdf','xlsx'])cases.push({version:1,id:process.env.P5A_HISTORICAL_ID,view:'shift-summary',format});
  for(const item of cases){
   const {version,id,view,format}=item;
   if(version===1){const show=panel.getByRole('button',{name:'Show historical report versions',exact:true});if(await show.count())await show.click();}
   const group=panel.getByRole('group',{name:`Download controls for report version ${version}`,exact:true});
   await group.getByRole('combobox',{name:`View for report version ${version}`,exact:true}).selectOption(view);
   await group.getByRole('combobox',{name:`Format for report version ${version}`,exact:true}).selectOption(format);
   if(version===1)await expect(group.getByRole('note')).toContainText('Historical report snapshot');
   const downloadEvent=page.waitForEvent('download');
   const responseEvent=page.waitForResponse(r=>r.url().includes(`/reports/${id}/export?`));
   await group.getByRole('button',{name:`Download report version ${version}`,exact:true}).click();
   const [download,response]=await Promise.all([downloadEvent,responseEvent]);
   expect(response.status()).toBe(200);expect(response.headers()['cache-control']).toBe('no-store');
   expect(response.headers()['x-content-type-options']).toBe('nosniff');
   const filename=`report-${id}-v${version}-${view}.${format}`;expect(download.suggestedFilename()).toBe(filename);
   const file=path.join(process.env.P5A_PROOF_DIR,filename);await download.saveAs(file);expect(await download.failure()).toBe(null);
   await expect(group.getByRole('status')).toHaveText(`Download started for report version ${version}.`);
   const bytes=fs.readFileSync(file);results.push({...item,filename,bytes:bytes.length,sha256:crypto.createHash('sha256').update(bytes).digest('hex'),mime:response.headers()['content-type']});fs.writeFileSync(path.join(process.env.P5A_PROOF_DIR,'browser-progress.json'),JSON.stringify(results,null,2));
  }
  await expect.poll(async()=>await page.evaluate(()=>window.__proof.revoked.length)).toBe(cases.length);
  const observed=await page.evaluate(()=>window.__proof);
  expect(observed.created.length).toBe(cases.length);expect(new Set(observed.revoked).size).toBe(cases.length);
  expect(observed.headers.every(h=>h.disposition===null)).toBe(true);
  expect(await page.locator('a[download]').count()).toBe(0);
  const current=panel.getByRole('group',{name:'Download controls for report version 2',exact:true});
  await context.setOffline(true);await current.getByRole('button',{name:'Download report version 2',exact:true}).click();
  await expect(current.getByRole('alert')).toContainText('offline');
  expect(await page.evaluate(()=>window.__proof.created.length)).toBe(cases.length);
  await context.setOffline(false);
  await panel.screenshot({path:path.join(process.env.P5A_PROOF_DIR,'download-panel.png')});
  expect(errors).toEqual([]);
  console.log(JSON.stringify({downloads:results,urlsCreated:observed.created.length,urlsRevoked:observed.revoked.length,corsHiddenDisposition:true,offlineRefusedWithoutDownload:true,pageErrors:errors.length,browserVersion:browser.version()}));
 }finally{await context.close();await browser.close();}
})().catch(e=>{console.error(e.stack);process.exitCode=1;});
"""


def verify_download_bytes(out, reports, downloads):
    import re

    import fitz
    from openpyxl import load_workbook

    by_id = {r["report_id"]: r for r in reports}
    views = {
        "customer-report": "customer_requests",
        "incident-report": "incidents",
        "handover-report": "handovers",
    }
    labels = {
        "DRAFT": "Draft",
        "IN_REVIEW": "In review",
        "APPROVED": "Approved",
        "FROZEN": "Frozen",
    }
    for item in downloads:
        report = by_id[item["id"]]
        sections = [
            s
            for s in report["sections"]
            if item["view"] == "shift-summary" or s["section_type"] == views[item["view"]]
        ]
        expected = sorted(
            (r["record_type"], r["record_id"]) for s in sections for r in s["records"]
        )
        path = out / item["filename"]
        if item["format"] == "pdf":
            with fitz.open(path) as doc:
                text = "\n".join(p.get_text() for p in doc)
            actual = sorted(re.findall(r"^Record: (\w+)/([0-9a-f-]{36})$", text, re.MULTILINE))
            assert actual == expected, (path.name, actual, expected)
            assert report["report_id"] in text and report["snapshot_digest"] in text
            assert labels[report["status"]] in text
            assert ("Historical:" in text) == (not report["is_current"])
            assert "\ufffd" not in text
        else:
            wb = load_workbook(path, data_only=False)
            pairs = list(wb["Content"].values)
            actual = sorted(tuple(str(v).split("/", 1)) for k, v in pairs if k == "Record")
            assert actual == expected, (path.name, actual, expected)
            meta = dict(wb["Metadata"].values)
            assert meta["report_id"] == report["report_id"]
            assert meta["snapshot_digest"] == report["snapshot_digest"]
            assert str(meta["version"]) == str(report["version"])
            for sheet in wb:
                for row in sheet:
                    assert all(c.data_type != "f" and c.hyperlink is None for c in row)
            assert not wb._external_links
            wb.close()


def selected_sources(root):
    """Digest declared product and harness files; no whole-repository scan claim."""
    import hashlib

    patterns = (
        "tests/integration/test_report_export_browser*.py",
        "packages/reporting-engine/src/reporting_engine/**/*.py",
        "packages/reporting-engine/src/reporting_engine/assets/*",
        "packages/operations-domain/src/operations_domain/report_digest.py",
        "apps/workspace-api/src/workspace_api/application/report_export*.py",
        "apps/workspace-api/src/workspace_api/application/report_snapshot.py",
        "apps/workspace-api/src/workspace_api/api/reports/router.py",
        "apps/workspace-web/src/features/operator-actions/Report*.tsx",
        "apps/workspace-web/src/services/api.ts",
        "apps/workspace-web/src/services/reportExport.ts",
    )
    files = {p for pattern in patterns for p in root.glob(pattern) if p.is_file()}
    return {
        p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(files)
    }


def isolated_environment(root):
    """Pass only OS/runtime paths; reject dotenv loading without reading secrets."""
    import os

    assert not [p for p in root.glob(".env*") if p.name != ".env.example"], "Root dotenv files"
    web = root / "apps/workspace-web"
    assert not [p for p in web.glob(".env*") if p.name != ".env.example"], "Web dotenv files"
    allowed = {
        "SYSTEMROOT",
        "WINDIR",
        "COMSPEC",
        "PATH",
        "PATHEXT",
        "TEMP",
        "TMP",
        "LOCALAPPDATA",
        "APPDATA",
        "USERPROFILE",
        "HOMEDRIVE",
        "HOMEPATH",
        "PROGRAMFILES",
        "PROGRAMFILES(X86)",
        "PROGRAMDATA",
    }
    return {k: v for k, v in os.environ.items() if k.upper() in allowed}
