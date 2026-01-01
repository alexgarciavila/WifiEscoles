# Script para validar y actualizar el checklist pre-implementación
# Genera un reporte de validación basado en la documentación

$checklistPath = "specs\001-dark-theme-mode\checklists\pre-implementation.md"
$reportPath = "specs\001-dark-theme-mode\checklists\validation-report.md"

Write-Host "Generando reporte de validación del checklist..." -ForegroundColor Cyan

# Leer checklist actual
$content = Get-Content $checklistPath -Raw

# Análisis de items completados vs pendientes
$totalItems = ([regex]::Matches($content, "- \[.\] CHK\d+")).Count
$completedItems = ([regex]::Matches($content, "- \[x\] CHK\d+")).Count
$pendingItems = $totalItems - $completedItems

# Calcular porcentaje
$completionPercentage = [math]::Round(($completedItems / $totalItems) * 100, 2)

# Generar reporte
$report = @"
# Reporte de Validación del Checklist Pre-Implementación

**Fecha**: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
**Feature**: 001-dark-theme-mode

## Resumen Ejecutivo

- **Total de Items**: $totalItems
- **Items Completados**: $completedItems
- **Items Pendientes**: $pendingItems
- **Porcentaje de Completitud**: $completionPercentage%

## Análisis por Categoría

"@

# Extraer gaps identificados
$gaps = @"

### Gaps Críticos Identificados

Los siguientes items marcados como GAP requieren decisión:

"@

# Buscar todos los GAP en el contenido
$gapPattern = '- \[ \] (CHK\d+).*\[Gap\]'
$gapMatches = [regex]::Matches($content, $gapPattern)

foreach ($match in $gapMatches) {
    $itemNum = $match.Groups[1].Value
    $gaps += "- $itemNum`: Requiere especificación de requisito formal`n"
}

$report += $gaps

# Guardar reporte
$report | Out-File $reportPath -Encoding UTF8

Write-Host "`n✅ Reporte generado en: $reportPath" -ForegroundColor Green
Write-Host "`nEstadísticas:" -ForegroundColor Yellow
Write-Host "  Completados: $completedItems / $totalItems ($completionPercentage%)" -ForegroundColor Green
Write-Host "  Pendientes: $pendingItems" -ForegroundColor Yellow

# Mostrar mensaje según completitud
if ($completionPercentage -eq 100) {
    Write-Host "`n🎉 ¡Checklist 100% validado! Listo para implementación." -ForegroundColor Green
} elseif ($completionPercentage -gt 80) {
    Write-Host "`n⚠️  Checklist casi completo. Revisar items pendientes antes de implementación." -ForegroundColor Yellow
} else {
    Write-Host "`n⛔ Checklist requiere más validación antes de proceder." -ForegroundColor Red
}
