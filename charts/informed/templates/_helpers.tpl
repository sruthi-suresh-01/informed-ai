{{/*
Expand the name of the chart.
*/}}
{{- define "informed-core.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "informed-core.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "informed-core.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "informed-core.labels" -}}
helm.sh/chart: {{ include "informed-core.chart" . }}
{{ include "informed-core.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "informed-core.selectorLabels" -}}
app.kubernetes.io/name: {{ include "informed-core.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "informed-core.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "informed-core.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{- define "local-tls-cert" -}}
{{- $caCrt := .Files.Get "localCerts/informedCA.crt" | b64enc }}
{{- $caKey := .Files.Get "localCerts/informedCA.key" | b64enc }}
{{- $ca := buildCustomCert $caCrt $caKey -}}
{{- $cert := genSignedCert "local.app.informed.com" nil (list "local.app.informed.com") 365 $ca -}}
tls.crt: {{ $cert.Cert | b64enc }}
tls.key: {{ $cert.Key | b64enc }}
{{- end -}}

{{- define "dbUrl" -}}
{{- if .Values.postgresql.urlSecretName }}
valueFrom:
  secretKeyRef:
    name: {{ .Values.postgresql.urlSecretName }}
    key: value
{{- else if .Values.postgresql.enabled }}
value: postgresql+psycopg://{{.Values.global.postgresql.auth.username }}:{{.Values.global.postgresql.auth.password }}@{{ .Values.global.postgresql.host }}:{{.Values.global.postgresql.port }}/{{.Values.global.postgresql.auth.database }}
{{- else }}
{{- fail "Either postgresql.urlSecretName must be provided or postgres.enabled needs to be set to true" }}
{{- end }}
{{- end }}
