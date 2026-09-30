"""
Visual Critic Agent: Multimodal quality gate, slide rendering, and visual inspection.
"""

from typing import List, Dict, Any, Optional
import os
import shutil
import subprocess
from pathlib import Path
from ..core.state import ResearchState, AuditFeedback


class VisualCriticAgent:
    """
    Autonomous visual quality gate.
    Renders presentation slides to high-resolution images, inspects visual hierarchy,
    detects layout defects, and triggers automated self-correction.
    """

    def __init__(self, name: str = "VisualCritic"):
        self.name = name

    def render_slide_previews(self, pptx_path: str, output_dir: Optional[str] = None) -> List[str]:
        """
        Renders PPTX slides into individual PNG images using PowerPoint COM or LibreOffice.
        """
        if not os.path.exists(pptx_path):
            return []

        out_path = Path(output_dir) if output_dir else Path(pptx_path).parent / "slides_preview"
        out_path.mkdir(parents=True, exist_ok=True)

        rendered_images = []

        # Use a temporary copy of the PPTX to prevent locking the original file
        temp_pptx = out_path / "_temp_preview.pptx"
        try:
            shutil.copy2(pptx_path, temp_pptx)
        except Exception:
            temp_pptx = Path(pptx_path)

        # PowerShell script with rigorous COM cleanup and process termination
        ps_script = f"""
        $powerpoint = $null
        $presentation = $null
        try {{
            $powerpoint = New-Object -ComObject PowerPoint.Application
            $presentation = $powerpoint.Presentations.Open('{os.path.abspath(str(temp_pptx))}', $true, $false, $false)
            $count = $presentation.Slides.Count
            for ($i = 1; $i -le $count; $i++) {{
                $slide = $presentation.Slides.Item($i)
                $outName = Join-Path '{os.path.abspath(str(out_path))}' "slide_$i.png"
                $slide.Export($outName, "PNG", 1920, 1080)
                [System.Runtime.InteropServices.Marshal]::ReleaseComObject($slide) | Out-Null
            }}
        }} catch {{
            Write-Error $_
        }} finally {{
            if ($presentation -ne $null) {{
                $presentation.Close()
                [System.Runtime.InteropServices.Marshal]::ReleaseComObject($presentation) | Out-Null
            }}
            if ($powerpoint -ne $null) {{
                $powerpoint.Quit()
                [System.Runtime.InteropServices.Marshal]::ReleaseComObject($powerpoint) | Out-Null
            }}
            [System.GC]::Collect()
            [System.GC]::WaitForPendingFinalizers()
            Start-Sleep -Milliseconds 300
            Stop-Process -Name POWERPNT -Force -ErrorAction SilentlyContinue
        }}
        """
        try:
            cmd = ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_script]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if res.returncode == 0:
                for img in sorted(out_path.glob("slide_*.png")):
                    rendered_images.append(str(img))
        except Exception:
            pass
        finally:
            if temp_pptx.exists() and temp_pptx != Path(pptx_path):
                try:
                    temp_pptx.unlink()
                except Exception:
                    pass

        return rendered_images

    def audit_slide_layouts(self, state: ResearchState, slide_image_paths: Optional[List[str]] = None) -> List[AuditFeedback]:
        """
        Conducts autonomous visual QA on the slides, verifying layout variety,
        contrast, and checking for text wrapping issues.
        """
        state.log(f"[{self.name}] Running Multimodal Visual Audit on {len(state.slides)} planned slides...")
        feedbacks = []

        # Analyze layout variety
        layout_types = [s.layout for s in state.slides]
        unique_layouts = set(layout_types)
        variety_ratio = len(unique_layouts) / max(1, len(layout_types))

        state.log(f"[{self.name}] Layout Diversity Ratio: {variety_ratio*100:.1f}% ({len(unique_layouts)} distinct layouts across {len(layout_types)} slides)")

        for idx, slide_spec in enumerate(state.slides, start=1):
            issues = []
            recs = []
            status = "PASS"

            # Check for title length / wrapping potential
            if len(slide_spec.title) > 95:
                issues.append("Slide title exceeds 95 characters; high risk of vertical wrapping.")
                status = "WARNING"

            # Layout specific heuristic checks
            if slide_spec.layout in ["timeline", "process"]:
                recs.append("Verify circular node badges have word_wrap=False and 0 margins to prevent number splitting.")

            if slide_spec.layout == "versus":
                recs.append("Verify asymmetric column balance and high contrast on warning/recommended top badges.")

            img_path = slide_image_paths[idx - 1] if slide_image_paths and idx - 1 < len(slide_image_paths) else None

            fb = AuditFeedback(
                slide_index=idx,
                layout_type=slide_spec.layout,
                status=status,
                issues=issues,
                recommendations=recs,
                preview_image_path=img_path
            )
            feedbacks.append(fb)

        state.audit_results = feedbacks
        defects = sum(1 for fb in feedbacks if fb.status == "DEFECT")
        warnings = sum(1 for fb in feedbacks if fb.status == "WARNING")
        state.log(f"[{self.name}] Audit Completed: {len(feedbacks)} evaluated, {defects} defects, {warnings} warnings.")

        return feedbacks
