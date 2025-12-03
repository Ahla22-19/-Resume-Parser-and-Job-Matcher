import React, { useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Typography,
  TextField,
  CircularProgress,
  Alert,
  Grid,
  Paper,
  Chip,
  Divider,
  IconButton
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import DescriptionIcon from '@mui/icons-material/Description';
import axios from 'axios';
import { styled } from '@mui/material/styles';

const VisuallyHiddenInput = styled('input')({
  clip: 'rect(0 0 0 0)',
  clipPath: 'inset(50%)',
  height: 1,
  overflow: 'hidden',
  position: 'absolute',
  bottom: 0,
  left: 0,
  whiteSpace: 'nowrap',
  width: 1,
});

const API_BASE_URL = 'http://localhost:8000';

const ResumeParser = ({ onResumeParsed }) => {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [parsedData, setParsedData] = useState(null);

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile) {
      if (selectedFile.type !== 'application/pdf' && 
          selectedFile.type !== 'application/vnd.openxmlformats-officedocument.wordprocessingml.document') {
        setError('Please upload a PDF or DOCX file');
        return;
      }
      setFile(selectedFile);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file first');
      return;
    }

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(`${API_BASE_URL}/parse-resume`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data.success) {
        const data = response.data.data;
        setParsedData(data);
        
        // Create session
        const sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        
        // Create chat agent with resume data
        await axios.post(`${API_BASE_URL}/create-agent/${sessionId}`, data);
        
        onResumeParsed(data, sessionId);
      } else {
        setError(response.data.message || 'Failed to parse resume');
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred while uploading the file');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setFile(null);
    setParsedData(null);
    setError(null);
  };

  return (
    <Box sx={{ maxWidth: 800, mx: 'auto' }}>
      <Card>
        <CardContent>
          <Typography variant="h5" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <DescriptionIcon /> Resume Parser
          </Typography>
          
          <Typography variant="body2" color="text.secondary" paragraph>
            Upload your resume (PDF or DOCX) to automatically extract your information
          </Typography>

          {!parsedData ? (
            <Box sx={{ mt: 3 }}>
              <Paper
                variant="outlined"
                sx={{
                  p: 4,
                  textAlign: 'center',
                  border: '2px dashed #ccc',
                  backgroundColor: 'background.default',
                  cursor: 'pointer',
                  '&:hover': {
                    borderColor: 'primary.main',
                    backgroundColor: 'action.hover',
                  },
                }}
                onClick={() => document.getElementById('resume-upload').click()}
              >
                <CloudUploadIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                  Drag & drop or click to upload
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Supported formats: PDF, DOCX
                </Typography>
                <VisuallyHiddenInput
                  id="resume-upload"
                  type="file"
                  onChange={handleFileChange}
                  accept=".pdf,.docx"
                />
              </Paper>

              {file && (
                <Box sx={{ mt: 2, p: 2, bgcolor: 'success.light', borderRadius: 1 }}>
                  <Typography variant="body2">
                    Selected: <strong>{file.name}</strong> ({Math.round(file.size / 1024)} KB)
                  </Typography>
                </Box>
              )}

              {error && (
                <Alert severity="error" sx={{ mt: 2 }}>
                  {error}
                </Alert>
              )}

              <Box sx={{ mt: 3, display: 'flex', gap: 2, justifyContent: 'center' }}>
                <Button
                  variant="contained"
                  onClick={handleUpload}
                  disabled={!file || loading}
                  startIcon={loading ? <CircularProgress size={20} /> : null}
                >
                  {loading ? 'Parsing...' : 'Parse Resume'}
                </Button>
                
                {file && (
                  <Button variant="outlined" onClick={handleReset}>
                    Reset
                  </Button>
                )}
              </Box>
            </Box>
          ) : (
            <Box sx={{ mt: 2 }}>
              <Alert severity="success" sx={{ mb: 3 }}>
                Resume parsed successfully! Your information has been extracted.
              </Alert>

              <Grid container spacing={3}>
                <Grid item xs={12}>
                  <Typography variant="h6" gutterBottom>
                    Personal Information
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="Full Name"
                        value={parsedData.name || ''}
                        variant="outlined"
                        InputProps={{ readOnly: true }}
                      />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="Email"
                        value={parsedData.email || ''}
                        variant="outlined"
                        InputProps={{ readOnly: true }}
                      />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="Phone"
                        value={parsedData.phone || ''}
                        variant="outlined"
                        InputProps={{ readOnly: true }}
                      />
                    </Grid>
                  </Grid>
                </Grid>

                <Grid item xs={12}>
                  <Divider sx={{ my: 2 }} />
                  <Typography variant="h6" gutterBottom>
                    Skills
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                    {parsedData.skills.map((skill, index) => (
                      <Chip key={index} label={skill} color="primary" variant="outlined" />
                    ))}
                  </Box>
                </Grid>

                <Grid item xs={12}>
                  <Divider sx={{ my: 2 }} />
                  <Typography variant="h6" gutterBottom>
                    Work Experience
                  </Typography>
                  {parsedData.experience.map((exp, index) => (
                    <Box key={index} sx={{ mb: 2, p: 2, border: '1px solid #e0e0e0', borderRadius: 1 }}>
                      <Typography variant="subtitle1" fontWeight="bold">
                        {exp.title}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {exp.company} • {exp.start_date} - {exp.end_date || 'Present'}
                      </Typography>
                      {exp.description && (
                        <Typography variant="body2" sx={{ mt: 1 }}>
                          {exp.description}
                        </Typography>
                      )}
                    </Box>
                  ))}
                </Grid>

                <Grid item xs={12}>
                  <Divider sx={{ my: 2 }} />
                  <Typography variant="h6" gutterBottom>
                    Education
                  </Typography>
                  {parsedData.education.map((edu, index) => (
                    <Box key={index} sx={{ mb: 2, p: 2, border: '1px solid #e0e0e0', borderRadius: 1 }}>
                      <Typography variant="subtitle1" fontWeight="bold">
                        {edu.degree}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {edu.institution} • {edu.start_date} - {edu.end_date || 'Present'}
                      </Typography>
                      {edu.field_of_study && (
                        <Typography variant="body2">
                          Field: {edu.field_of_study}
                        </Typography>
                      )}
                    </Box>
                  ))}
                </Grid>
              </Grid>

              <Box sx={{ mt: 3, display: 'flex', justifyContent: 'center' }}>
                <Button variant="contained" onClick={() => onResumeParsed(parsedData, `session_${Date.now()}`)}>
                  Start Job Hunting →
                </Button>
              </Box>
            </Box>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export default ResumeParser;