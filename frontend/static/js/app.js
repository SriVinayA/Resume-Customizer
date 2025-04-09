document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const resumeForm = document.getElementById('resumeForm');
    const resumeInput = document.getElementById('resume');
    const fileNameSpan = document.querySelector('.file-name');
    const fileUploadLabel = document.querySelector('.file-upload-label');
    const submitBtn = document.getElementById('submitBtn');
    const spinner = document.getElementById('spinner');
    const pdfSpinner = document.getElementById('pdfSpinner');
    const resultsSection = document.getElementById('results');
    const downloadPdfBtn = document.getElementById('downloadPdfBtn');
    const editInOverleafBtn = document.getElementById('editInOverleafBtn');
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toastMessage');
    const toastClose = document.getElementById('toastClose');
    const loadingOverlay = document.getElementById('loadingOverlay');
    
    // API Base URL
    const API_BASE_URL = 'http://localhost:8000';
    
    // Store response data
    let responseData = null;
    
    // Event Listeners
    resumeInput.addEventListener('change', updateFileName);
    fileUploadLabel.addEventListener('click', () => resumeInput.click());
    resumeForm.addEventListener('submit', handleFormSubmit);
    downloadPdfBtn.addEventListener('click', handleDownloadPdf);
    editInOverleafBtn.addEventListener('click', handleEditInOverleaf);
    toastClose.addEventListener('click', hideToast);
    
    // Functions
    function updateFileName() {
        const fileName = resumeInput.files[0] ? resumeInput.files[0].name : 'No file chosen';
        fileNameSpan.textContent = fileName;
    }
    
    // Show/hide loading overlay with minimum display time
    function showLoadingOverlay(message) {
        const loadingText = document.querySelector('.loading-text');
        if (loadingText && message) {
            loadingText.textContent = message;
        }
        loadingOverlay.style.display = 'flex';
    }
    
    function hideLoadingOverlay(minimumTime = 0) {
        const startTime = loadingOverlay.dataset.startTime;
        const elapsedTime = startTime ? Date.now() - parseInt(startTime) : 0;
        const remainingTime = Math.max(0, minimumTime - elapsedTime);
        
        if (remainingTime > 0) {
            setTimeout(() => {
                loadingOverlay.style.display = 'none';
            }, remainingTime);
        } else {
            loadingOverlay.style.display = 'none';
        }
    }
    
    async function handleFormSubmit(e) {
        e.preventDefault();
        
        // Validate form
        if (!resumeInput.files[0]) {
            showToast('Please select a resume file', 'error');
            return;
        }
        
        const jobDescription = document.getElementById('jobDescription').value.trim();
        if (!jobDescription) {
            showToast('Please enter a job description', 'error');
            return;
        }
        
        // Show loading state with overlay
        submitBtn.disabled = true;
        showLoadingOverlay('Customizing Your Resume...');
        loadingOverlay.dataset.startTime = Date.now().toString();
        resultsSection.style.display = 'none';
        
        try {
            const formData = new FormData(resumeForm);
            
            const response = await fetch(`${API_BASE_URL}/customize-resume/`, {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(`Server responded with status: ${response.status}`);
            }
            
            responseData = await response.json();
            
            // Display the results
            displayResults(responseData);
            
            // Show success message
            showToast('Resume customized successfully!', 'success');
            
        } catch (error) {
            console.error('Error:', error);
            showToast(`Error: ${error.message}`, 'error');
        } finally {
            // Reset loading state with minimum display time
            submitBtn.disabled = false;
            hideLoadingOverlay(2000); // Ensure overlay shows for at least 2 seconds
        }
    }
    
    function displayResults(data) {
        if (!data || !data.customized_resume) {
            showToast('Invalid response from server', 'error');
            return;
        }
        
        const resume = data.customized_resume;
        
        // Display modifications summary
        const summaryElement = document.getElementById('modificationsSummary');
        if (resume.modifications_summary) {
            console.log("Modifications summary:", resume.modifications_summary); // Debug log
            
            let summaryContent = '';
            
            // Handle the new format with specific change categories
            const newFormatProperties = [
                { key: 'job_title_changes', title: 'Job Title Changes' },
                { key: 'skills_added', title: 'Skills Added/Modified' },
                { key: 'experience_rewrites', title: 'Experience Rewrites' },
                { key: 'projects_modified', title: 'Projects Modified' }
            ];
            
            let usedNewFormat = false;
            
            // Check if using the new format
            for (const prop of newFormatProperties) {
                if (resume.modifications_summary[prop.key] && 
                   (Array.isArray(resume.modifications_summary[prop.key]) || 
                    typeof resume.modifications_summary[prop.key] === 'string')) {
                    
                    usedNewFormat = true;
                    summaryContent += `<h4>${prop.title}:</h4><ul>`;
                    
                    if (Array.isArray(resume.modifications_summary[prop.key])) {
                        resume.modifications_summary[prop.key].forEach(item => {
                            if (typeof item === 'object' && item !== null) {
                                const itemText = item.text || item.description || item.value || JSON.stringify(item);
                                summaryContent += `<li>${itemText}</li>`;
                            } else {
                                summaryContent += `<li>${item}</li>`;
                            }
                        });
                    } else if (typeof resume.modifications_summary[prop.key] === 'string') {
                        summaryContent += `<li>${resume.modifications_summary[prop.key]}</li>`;
                    }
                    
                    summaryContent += '</ul>';
                }
            }
            
            // If we didn't use the new format, fall back to the old format handling
            if (!usedNewFormat) {
                if (resume.modifications_summary.changes_made && Array.isArray(resume.modifications_summary.changes_made)) {
                    summaryContent += '<h4>Changes Made:</h4><ul>';
                    resume.modifications_summary.changes_made.forEach(change => {
                        // Handle change if it's an object
                        if (typeof change === 'object' && change !== null) {
                            // Try to convert object to string or extract a meaningful property
                            const changeText = change.text || change.description || change.value || JSON.stringify(change);
                            summaryContent += `<li>${changeText}</li>`;
                        } else {
                            summaryContent += `<li>${change}</li>`;
                        }
                    });
                    summaryContent += '</ul>';
                } else if (resume.modifications_summary.changes && Array.isArray(resume.modifications_summary.changes)) {
                    summaryContent += '<h4>Changes Made:</h4><ul>';
                    resume.modifications_summary.changes.forEach(change => {
                        if (typeof change === 'string') {
                            summaryContent += `<li>${change}</li>`;
                        } else if (typeof change === 'object' && change !== null) {
                            if (change.action) {
                                summaryContent += `<li>${change.action}`;
                                if (change.reason) {
                                    summaryContent += ` <em>(${change.reason})</em>`;
                                }
                                summaryContent += `</li>`;
                            } else {
                                // Handle generic object by converting to string or extracting a property
                                const changeText = change.text || change.description || change.value || JSON.stringify(change);
                                summaryContent += `<li>${changeText}</li>`;
                            }
                        }
                    });
                    summaryContent += '</ul>';
                } else if (typeof resume.modifications_summary === 'string') {
                    summaryContent = `<p>${resume.modifications_summary}</p>`;
                } else if (typeof resume.modifications_summary === 'object' && resume.modifications_summary !== null) {
                    // If modifications_summary is a direct object, try to extract properties
                    if (resume.modifications_summary.changes || resume.modifications_summary.summary) {
                        const summaryText = resume.modifications_summary.changes || resume.modifications_summary.summary;
                        if (Array.isArray(summaryText)) {
                            summaryContent += '<h4>Changes Made:</h4><ul>';
                            summaryText.forEach(item => {
                                summaryContent += `<li>${item}</li>`;
                            });
                            summaryContent += '</ul>';
                        } else {
                            summaryContent += `<p>${summaryText}</p>`;
                        }
                    } else {
                        // Fallback to JSON.stringify for unknown object structure
                        try {
                            summaryContent += `<p>${JSON.stringify(resume.modifications_summary, null, 2)}</p>`;
                        } catch (e) {
                            summaryContent += '<p>Unable to display modification summary</p>';
                        }
                    }
                }
                
                if (resume.modifications_summary.reasons && Array.isArray(resume.modifications_summary.reasons)) {
                    summaryContent += '<h4>Reasons:</h4><ul>';
                    resume.modifications_summary.reasons.forEach(reason => {
                        // Handle reason if it's an object
                        if (typeof reason === 'object' && reason !== null) {
                            const reasonText = reason.text || reason.description || reason.value || JSON.stringify(reason);
                            summaryContent += `<li>${reasonText}</li>`;
                        } else {
                            summaryContent += `<li>${reason}</li>`;
                        }
                    });
                    summaryContent += '</ul>';
                } else if (resume.modifications_summary.reasoning) {
                    // Try alternate property name
                    summaryContent += '<h4>Reasoning:</h4><p>';
                    if (typeof resume.modifications_summary.reasoning === 'string') {
                        summaryContent += resume.modifications_summary.reasoning;
                    } else if (Array.isArray(resume.modifications_summary.reasoning)) {
                        summaryContent += '<ul>';
                        resume.modifications_summary.reasoning.forEach(reason => {
                            summaryContent += `<li>${reason}</li>`;
                        });
                        summaryContent += '</ul>';
                    }
                    summaryContent += '</p>';
                }
            }
            
            // If no content was generated, show a fallback message
            if (!summaryContent.trim()) {
                console.log("Empty summary content, using fallback"); // Debug log
                summaryContent = `<p>The resume has been customized for the job description. 
                    Details about specific changes are not available.</p>
                    <p><strong>Debug info:</strong> ${JSON.stringify(resume.modifications_summary)}</p>`;
            }
            
            summaryElement.innerHTML = summaryContent;
        } else {
            // Handle missing modifications_summary
            console.log("No modifications_summary found in the response"); // Debug log
            summaryElement.innerHTML = '<p>Your resume has been customized for the job description.</p>';
        }
        
        // Update PDF download button if PDF path is available
        if (data.pdf_path) {
            downloadPdfBtn.setAttribute('data-pdf-path', data.pdf_path);
            downloadPdfBtn.disabled = false;
            
            // Store custom filename if available
            if (data.custom_filename) {
                downloadPdfBtn.setAttribute('data-custom-filename', data.custom_filename);
            }
            
            // Show PDF generation success message
            showToast('Your customized resume PDF is ready to download!', 'success');
            
            // Extract LaTeX path from PDF path
            const pdfPath = data.pdf_path;
            const latexPath = pdfPath.replace('.pdf', '.tex');
            editInOverleafBtn.setAttribute('data-latex-path', latexPath);
            editInOverleafBtn.disabled = false;
        } else {
            downloadPdfBtn.disabled = true;
            editInOverleafBtn.disabled = true;
        }
        
        // Show results section
        resultsSection.style.display = 'block';
    }
    
    function handleDownloadPdf() {
        const pdfPath = downloadPdfBtn.getAttribute('data-pdf-path');
        
        if (!pdfPath) {
            showToast('PDF path not available. Please try regenerating the resume.', 'error');
            return;
        }
        
        // Get the custom filename if available, otherwise extract from path
        let filename;
        const customFilename = downloadPdfBtn.getAttribute('data-custom-filename');
        if (customFilename) {
            filename = customFilename;
        } else {
            // Extract the filename from the path as fallback
            filename = pdfPath.split('/').pop();
        }
        
        // Show loading state with overlay
        downloadPdfBtn.disabled = true;
        downloadPdfBtn.textContent = 'Generating PDF...';
        showLoadingOverlay('Preparing Your PDF...');
        loadingOverlay.dataset.startTime = Date.now().toString();
        
        // Create a download link for the PDF
        fetch(`${API_BASE_URL}/download-pdf/?path=${encodeURIComponent(pdfPath)}${customFilename ? `&custom_filename=${encodeURIComponent(customFilename)}` : ''}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('PDF download failed');
                }
                return response.blob();
            })
            .then(blob => {
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                
                // Hide loading state with minimum display time
                hideLoadingOverlay(1500);
                downloadPdfBtn.disabled = false;
                downloadPdfBtn.textContent = 'Download PDF';
                
                showToast('PDF downloaded successfully!', 'success');
            })
            .catch(error => {
                console.error('Download error:', error);
                showToast(`Error downloading PDF: ${error.message}`, 'error');
                
                // Fallback: open the PDF in a new tab
                window.open(`${API_BASE_URL}/view-pdf/?path=${encodeURIComponent(pdfPath)}`, '_blank');
                
                // Always hide loading overlay and reset button
                hideLoadingOverlay(0);
                downloadPdfBtn.disabled = false;
                downloadPdfBtn.textContent = 'Download PDF';
            });
    }
    
    function handleEditInOverleaf() {
        const pdfPath = downloadPdfBtn.getAttribute('data-pdf-path');
        
        if (!pdfPath) {
            showToast('PDF path not available. Please try regenerating the resume.', 'error');
            return;
        }
        
        // Show loading state
        editInOverleafBtn.disabled = true;
        editInOverleafBtn.textContent = 'Preparing...';
        showLoadingOverlay('Preparing LaTeX for Overleaf...');
        loadingOverlay.dataset.startTime = Date.now().toString();
        
        // Fetch the LaTeX file content
        fetch(`${API_BASE_URL}/view-latex/?path=${encodeURIComponent(pdfPath)}`)
            .then(response => {
                if (!response.ok) {
                    if (response.status === 404) {
                        throw new Error('LaTeX file not found. The system cannot locate the source file.');
                    } else if (response.status === 400) {
                        throw new Error('Invalid file path provided.');
                    } else {
                        throw new Error(`Server error (${response.status}): ${response.statusText}`);
                    }
                }
                return response.text();
            })
            .then(latexContent => {
                // Create a form to post to Overleaf
                const form = document.createElement('form');
                form.method = 'POST';
                form.action = 'https://www.overleaf.com/docs';
                form.target = '_blank';
                
                // Add the LaTeX content as a base64 encoded "snip_uri"
                const input = document.createElement('input');
                input.type = 'hidden';
                input.name = 'snip_uri';
                
                // Create a ZIP-like structure with the LaTeX content
                // This is a simplified version - in a real implementation, you'd want
                // to create an actual ZIP with the proper structure
                const encodedContent = btoa(unescape(encodeURIComponent(latexContent)));
                input.value = `data:application/x-tex;base64,${encodedContent}`;
                
                form.appendChild(input);
                document.body.appendChild(form);
                
                // Hide loading state
                hideLoadingOverlay(1000);
                editInOverleafBtn.disabled = false;
                editInOverleafBtn.textContent = 'Edit in Overleaf 🍃';
                
                // Submit the form
                form.submit();
                
                // Clean up the form
                document.body.removeChild(form);
            })
            .catch(error => {
                console.error('Overleaf error:', error);
                showToast(`Error preparing for Overleaf: ${error.message}`, 'error');
                
                // Reset button state
                hideLoadingOverlay(0);
                editInOverleafBtn.disabled = false;
                editInOverleafBtn.textContent = 'Edit in Overleaf 🍃';
            });
    }
    
    function showToast(message, type = 'info') {
        toastMessage.textContent = message;
        toast.className = 'toast';
        toast.classList.add(`toast-${type}`);
        toast.style.display = 'flex';
        
        // Auto hide after 5 seconds
        setTimeout(hideToast, 5000);
    }
    
    function hideToast() {
        toast.style.display = 'none';
    }
}); 