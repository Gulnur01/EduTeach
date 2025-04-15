const accordion = document.querySelector('.accordion');
        const accordionHeader = document.querySelector('.accordion-header');

        accordionHeader.addEventListener('click', () => {
            accordion.classList.toggle('active');
        });

        // Добавляем обработчик для подсветки строк при наведении
        document.querySelectorAll('tr').forEach(row => {
            row.addEventListener('mouseover', () => {
                if (!row.querySelector('th') && !row.querySelector('.table-header')) {
                    const cells = row.getElementsByTagName('td');
                    for (let cell of cells) {
                        cell.style.backgroundColor = '#f5f5f5';
                    }
                }
            });
            
            row.addEventListener('mouseout', () => {
                if (!row.querySelector('th') && !row.querySelector('.table-header')) {
                    const cells = row.getElementsByTagName('td');
                    for (let cell of cells) {
                        cell.style.backgroundColor = '';
                    }
                }
            });
        });